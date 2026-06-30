"""Composition root.

Único módulo fuera de las capas de domain/application/infrastructure/interface;
es el único lugar que conoce tanto los adapters concretos (infrastructure) como
los routers (interface) y los cablea entre sí. Ver ADR-001.
"""

import asyncio
import contextlib
import logging
import os
import sys
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from datetime import date, timedelta

import structlog
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.auth.jwt_auth_provider import JwtAuthProvider
from infrastructure.crypto.fernet_pii_cipher import FernetPiiCipher
from infrastructure.epec.epec_factura_verificacion import EpecFacturaVerificacion
from infrastructure.fakes.medicion_horaria_source_reader import FakeMedicionHorariaSourceReader
from infrastructure.fakes.notification_sender import FakeNotificationSender
from infrastructure.smtp.notification_sender import SmtpNotificationSender
from infrastructure.sqlite.cached_vecinos_repository import CachedVecinosRepository
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from infrastructure.sqlite.consumo_horario_repository import SQLiteConsumoHorarioRepository
from infrastructure.sqlite.cuenta_sensible_repository import SQLiteCuentaSensibleRepository
from infrastructure.sqlite.notificacion_config_repository import SQLiteNotificacionConfigRepository
from infrastructure.sqlite.objetivo_consumo_repository import SQLiteObjetivoConsumoRepository
from infrastructure.sqlite.proyeccion_repository import SQLiteProyeccionRepository
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository
from infrastructure.sqlite.usuario_repository import SQLiteUsuarioRepository
from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository
from interface.alertas_router import router as alertas_router
from interface.auth_router import router as auth_router
from interface.consumo_router import router as consumo_router
from interface.cuenta_router import router as cuenta_router
from interface.dependencies import (
    get_auth_provider,
    get_consumo_horario_repo,
    get_consumo_repo,
    get_cuenta_reader,
    get_cuenta_sensible_repo,
    get_factura_reader,
    get_factura_verificacion,
    get_medicion_reader,
    get_notificacion_config_repo,
    get_notification_sender,
    get_objetivo_repo,
    get_pii_cipher,
    get_poblar_use_case,
    get_proyeccion_repo,
    get_suministro_repo,
    get_usuario_repo,
    get_vecinos_repo,
)
from interface.factura_router import build_router as build_factura_router
from interface.home_router import router as home_router
from interface.ingest_router import router as ingest_router
from interface.objetivos_router import router as objetivos_router


def _configure_logging() -> None:
    log_format = os.environ.get("LOG_FORMAT", "text")
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)


_configure_logging()

_ORACLE_VARS = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")


def _parse_env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def _parse_env_date(name: str, default: date) -> date:
    raw = os.environ.get(name)
    if raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            pass
    return default


def create_app() -> FastAPI:
    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///epec.db")
    engine = create_async_engine(db_url, echo=False)

    if db_url.startswith("sqlite"):
        from sqlalchemy import event

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragmas(dbapi_conn: object, _: object) -> None:
            from typing import Any

            conn: Any = dbapi_conn
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    oracle_available = all(os.environ.get(v) for v in _ORACLE_VARS)
    oracle_reader = None
    oracle_horaria_reader = None
    _oracle_vecinos = None
    _poblar_use_case = None
    _meta_reader = None
    _selector = None
    _cuenta_reader = None
    _factura_ids_reader = None
    if oracle_available:
        # Registra el dir de Instant Client para DLL search (os.add_dll_directory
        # actúa en el proceso actual — os.environ["PATH"] no es suficiente en Windows)
        instant_client = os.environ.get("OR_INSTANT_CLIENT", "")
        if instant_client and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(instant_client)

        from infrastructure.oracle.cuenta_reader import OracleCuentaReader
        from infrastructure.oracle.factura_identificadores_reader import (
            OracleFacturaIdentificadoresReader,
        )
        from infrastructure.oracle.ingestion_strategy_selector import IngestionStrategySelector
        from infrastructure.oracle.medicion_horaria_reader import OracleMedicionHorariaReader
        from infrastructure.oracle.medicion_reader import OracleMedicionReader
        from infrastructure.oracle.strategies.chupete_strategy import ChupeteIngestionStrategy
        from infrastructure.oracle.strategies.clou_strategy import ClouIngestionStrategy
        from infrastructure.oracle.strategies.nansen_strategy import NansenIngestionStrategy
        from infrastructure.oracle.suministro_meta_reader import OracleSuministroMetaReader
        from infrastructure.oracle.vecinos_repository import OracleVecinosRepository
        from infrastructure.orchestration.poblar_suministro import PoblarSuministroUseCase

        oracle_reader = OracleMedicionReader()
        oracle_horaria_reader = OracleMedicionHorariaReader()
        _oracle_vecinos = OracleVecinosRepository()

        _selector = IngestionStrategySelector(
            clou=ClouIngestionStrategy(),
            nansen=NansenIngestionStrategy(),
            chupete=ChupeteIngestionStrategy(),
        )
        _meta_reader = OracleSuministroMetaReader()
        _cuenta_reader = OracleCuentaReader()
        _factura_ids_reader = OracleFacturaIdentificadoresReader()

    def _build_notification_sender() -> SmtpNotificationSender | FakeNotificationSender:
        smtp_host = os.environ.get("SMTP_HOST")
        if not smtp_host:
            return FakeNotificationSender()
        return SmtpNotificationSender(
            host=smtp_host,
            port=_parse_env_int("SMTP_PORT", 587),
            username=os.environ.get("SMTP_USER"),
            password=os.environ.get("SMTP_PASS"),
            from_addr=os.environ.get("SMTP_FROM", f"alertas@{smtp_host}"),
            use_tls=os.environ.get("SMTP_TLS", "").lower() in ("1", "true", "yes"),
        )

    def _parse_env_equipos(name: str) -> list[str] | None:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return None
        return [e.strip() for e in raw.split(",") if e.strip()]

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        from infrastructure.sqlite.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        _horaria_reader = (
            oracle_horaria_reader
            if oracle_horaria_reader is not None
            else FakeMedicionHorariaSourceReader()
        )

        scheduler_task: asyncio.Task[None] | None = None
        if oracle_reader is not None:
            from infrastructure.ingestion_scheduler import run_scheduler

            desde_inicial = _parse_env_date(
                "INGEST_DESDE_INICIAL", date.today() - timedelta(days=90)
            )
            lookback_dias = _parse_env_int("INGEST_LOOKBACK_DIAS", 3)
            interval_horas = _parse_env_int("INGEST_INTERVAL_HORAS", 6)
            equipos = _parse_env_equipos("INGEST_EQUIPOS")

            scheduler_task = asyncio.create_task(
                run_scheduler(
                    oracle_reader,
                    session_factory,
                    desde_inicial=desde_inicial,
                    lookback_dias=lookback_dias,
                    interval_horas=interval_horas,
                    equipos=equipos,
                    notification_sender=_build_notification_sender(),
                    oracle_vecinos=_oracle_vecinos,
                    horaria_reader=_horaria_reader,
                )
            )
        yield
        if scheduler_task is not None:
            scheduler_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await scheduler_task

    epec_factura_base_url = os.environ.get("EPEC_FACTURA_BASE_URL")

    app = FastAPI(title="Plataforma de Clientes EPEC", lifespan=lifespan)
    app.include_router(auth_router)
    app.include_router(alertas_router)
    app.include_router(consumo_router)
    app.include_router(cuenta_router)
    app.include_router(home_router)
    app.include_router(ingest_router)
    app.include_router(objetivos_router)
    app.include_router(build_factura_router(epec_base_url=epec_factura_base_url))

    secret_key = os.environ["SECRET_KEY"]
    app.dependency_overrides[get_auth_provider] = lambda: JwtAuthProvider(secret_key=secret_key)

    async def _get_consumo_repo() -> AsyncGenerator[SQLiteConsumoDiarioRepository, None]:
        async with session_factory() as session:
            yield SQLiteConsumoDiarioRepository(session)

    async def _get_vecinos_repo() -> AsyncGenerator[SQLiteVecinosRepository, None]:
        async with session_factory() as session:
            yield SQLiteVecinosRepository(session)

    async def _get_proyeccion_repo() -> AsyncGenerator[SQLiteProyeccionRepository, None]:
        async with session_factory() as session:
            yield SQLiteProyeccionRepository(session)

    async def _get_suministro_repo() -> AsyncGenerator[SQLiteSuministroRepository, None]:
        async with session_factory() as session:
            yield SQLiteSuministroRepository(session)

    async def _get_usuario_repo() -> AsyncGenerator[SQLiteUsuarioRepository, None]:
        async with session_factory() as session:
            yield SQLiteUsuarioRepository(session)

    async def _get_notificacion_config_repo() -> AsyncGenerator[
        SQLiteNotificacionConfigRepository, None
    ]:
        async with session_factory() as session:
            yield SQLiteNotificacionConfigRepository(session)

    async def _get_objetivo_repo() -> AsyncGenerator[SQLiteObjetivoConsumoRepository, None]:
        async with session_factory() as session:
            yield SQLiteObjetivoConsumoRepository(session)

    async def _get_cuenta_sensible_repo() -> AsyncGenerator[SQLiteCuentaSensibleRepository, None]:
        async with session_factory() as session:
            yield SQLiteCuentaSensibleRepository(session)

    async def _get_consumo_horario_repo() -> AsyncGenerator[SQLiteConsumoHorarioRepository, None]:
        async with session_factory() as session:
            yield SQLiteConsumoHorarioRepository(session)

    _notification_sender = _build_notification_sender()
    _factura_verificacion = EpecFacturaVerificacion()
    app.dependency_overrides[get_notification_sender] = lambda: _notification_sender
    app.dependency_overrides[get_factura_verificacion] = lambda: _factura_verificacion

    if _factura_ids_reader is not None:
        from infrastructure.epec.epec_documentos_source_reader import EpecDocumentosSourceReader
        from infrastructure.sqlite.factura_identificadores_cache import (
            SQLiteFacturaIdentificadoresCache,
        )

        _ids_reader = _factura_ids_reader

        async def _get_factura_reader() -> AsyncGenerator[EpecDocumentosSourceReader, None]:
            async with session_factory() as session:
                yield EpecDocumentosSourceReader(
                    cache=SQLiteFacturaIdentificadoresCache(session),
                    identificadores_reader=_ids_reader,
                )

        app.dependency_overrides[get_factura_reader] = _get_factura_reader
    else:
        # Sin Oracle no hay factura real: 503 explícito (ADR-002), nunca deuda inventada.
        def _factura_no_configurada() -> None:
            raise HTTPException(
                status_code=503,
                detail="Factura no disponible — Oracle no configurado "
                "(definir OR_HOST, OR_USER, OR_PASS, OR_SERVICE_NAME)",
            )

        app.dependency_overrides[get_factura_reader] = _factura_no_configurada
    app.dependency_overrides[get_consumo_repo] = _get_consumo_repo
    app.dependency_overrides[get_consumo_horario_repo] = _get_consumo_horario_repo
    app.dependency_overrides[get_objetivo_repo] = _get_objetivo_repo
    app.dependency_overrides[get_cuenta_sensible_repo] = _get_cuenta_sensible_repo
    app.dependency_overrides[get_pii_cipher] = lambda: FernetPiiCipher(secret_key=secret_key)
    app.dependency_overrides[get_vecinos_repo] = _get_vecinos_repo
    app.dependency_overrides[get_proyeccion_repo] = _get_proyeccion_repo
    app.dependency_overrides[get_suministro_repo] = _get_suministro_repo
    app.dependency_overrides[get_usuario_repo] = _get_usuario_repo
    app.dependency_overrides[get_notificacion_config_repo] = _get_notificacion_config_repo

    if oracle_reader is not None:
        from infrastructure.ingestion_scheduler import _NonBlockingReader

        _non_blocking_reader = _NonBlockingReader(oracle_reader)
        app.dependency_overrides[get_medicion_reader] = lambda: _non_blocking_reader

        async def _get_cached_vecinos_repo() -> AsyncGenerator[CachedVecinosRepository, None]:
            async with session_factory() as session:
                assert _oracle_vecinos is not None
                yield CachedVecinosRepository(_oracle_vecinos, session)

        app.dependency_overrides[get_vecinos_repo] = _get_cached_vecinos_repo

        assert _oracle_vecinos is not None
        assert _meta_reader is not None
        assert _selector is not None
        _poblar_use_case = PoblarSuministroUseCase(
            meta_reader=_meta_reader,
            selector=_selector,
            vecinos_repo=_oracle_vecinos,
            session_factory=session_factory,
            bulk_reader=_non_blocking_reader,
        )
        app.dependency_overrides[get_poblar_use_case] = lambda: _poblar_use_case

        assert _cuenta_reader is not None
        app.dependency_overrides[get_cuenta_reader] = lambda: _cuenta_reader
    else:

        def _oracle_no_configurado() -> None:
            raise HTTPException(
                status_code=503,
                detail="Oracle no configurado — definir OR_HOST, OR_USER, OR_PASS, OR_SERVICE_NAME",
            )

        app.dependency_overrides[get_medicion_reader] = _oracle_no_configurado
        app.dependency_overrides[get_cuenta_reader] = _oracle_no_configurado
        app.dependency_overrides[get_poblar_use_case] = _oracle_no_configurado

    return app
