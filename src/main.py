"""Composition root.

Único módulo fuera de las capas de domain/application/infrastructure/interface;
es el único lugar que conoce tanto los adapters concretos (infrastructure) como
los routers (interface) y los cablea entre sí. Ver ADR-001.
"""

import asyncio
import contextlib
import logging
import os
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.auth.jwt_auth_provider import JwtAuthProvider
from infrastructure.fakes.notification_sender import FakeNotificationSender
from infrastructure.smtp.notification_sender import SmtpNotificationSender
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from infrastructure.sqlite.notificacion_config_repository import SQLiteNotificacionConfigRepository
from infrastructure.sqlite.objetivo_consumo_repository import SQLiteObjetivoConsumoRepository
from infrastructure.sqlite.proyeccion_repository import SQLiteProyeccionRepository
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository
from infrastructure.sqlite.usuario_repository import SQLiteUsuarioRepository
from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository
from interface.alertas_router import router as alertas_router
from interface.auth_router import router as auth_router
from interface.consumo_router import router as consumo_router
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_medicion_reader,
    get_notificacion_config_repo,
    get_objetivo_repo,
    get_proyeccion_repo,
    get_suministro_repo,
    get_usuario_repo,
    get_vecinos_repo,
)
from interface.factura_router import build_router as build_factura_router
from interface.home_router import router as home_router
from interface.ingest_router import router as ingest_router
from interface.objetivos_router import router as objetivos_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

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
    if oracle_available:
        # Registra el dir de Instant Client para DLL search (os.add_dll_directory
        # actúa en el proceso actual — os.environ["PATH"] no es suficiente en Windows)
        instant_client = os.environ.get("OR_INSTANT_CLIENT", "")
        if instant_client and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(instant_client)

        from infrastructure.oracle.medicion_reader import OracleMedicionReader

        oracle_reader = OracleMedicionReader()

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

    app.dependency_overrides[get_consumo_repo] = _get_consumo_repo
    app.dependency_overrides[get_objetivo_repo] = _get_objetivo_repo
    app.dependency_overrides[get_vecinos_repo] = _get_vecinos_repo
    app.dependency_overrides[get_proyeccion_repo] = _get_proyeccion_repo
    app.dependency_overrides[get_suministro_repo] = _get_suministro_repo
    app.dependency_overrides[get_usuario_repo] = _get_usuario_repo
    app.dependency_overrides[get_notificacion_config_repo] = _get_notificacion_config_repo

    if oracle_reader is not None:
        from infrastructure.ingestion_scheduler import _NonBlockingReader

        _non_blocking_reader = _NonBlockingReader(oracle_reader)
        app.dependency_overrides[get_medicion_reader] = lambda: _non_blocking_reader
    else:

        def _oracle_no_configurado() -> None:
            raise HTTPException(
                status_code=503,
                detail="Oracle no configurado — definir OR_HOST, OR_USER, OR_PASS, OR_SERVICE_NAME",
            )

        app.dependency_overrides[get_medicion_reader] = _oracle_no_configurado

    return app
