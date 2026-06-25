"""Caso de uso: poblar datos de un suministro desde Oracle hacia SQLite.

Orquesta: metadata → coordenadas/tarifa → vecinos_cache → lecturas (Strategy) → consumo_diario.
Se invoca como BackgroundTask después del login; crea sus propias sessions para
no depender del request context de FastAPI (que ya está cerrado al ejecutarse).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase
from domain.lecturas import LecturaTelemedida
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.vecinos_repository import VecinosRepository
from infrastructure.oracle.ingestion_strategy_selector import IngestionStrategySelector
from infrastructure.oracle.suministro_meta_reader import OracleSuministroMetaReader
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository
from infrastructure.sqlite.vecinos_cache_repository import SQLiteVecinosCacheRepository

logger = logging.getLogger(__name__)

_DIAS_HISTORICO = 400  # cubre año actual + año anterior completo para comparacion interanual


class _LecturasAdapter(MedicionSourceReader):
    """Adaptador que expone lecturas ya obtenidas como MedicionSourceReader."""

    def __init__(self, lecturas: list[LecturaTelemedida]) -> None:
        self._lecturas = lecturas

    async def leer_lecturas(
        self, desde: date, hasta: date, equipos: list[str] | None = None
    ) -> list[LecturaTelemedida]:
        return self._lecturas


class PoblarSuministroUseCase:
    def __init__(
        self,
        meta_reader: OracleSuministroMetaReader,
        selector: IngestionStrategySelector,
        vecinos_repo: VecinosRepository,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._meta_reader = meta_reader
        self._selector = selector
        self._vecinos_repo = vecinos_repo
        self._session_factory = session_factory

    async def ejecutar(self, suministro_id: str) -> None:
        logger.info("[PoblarSuministro] Iniciando para %s", suministro_id)

        # 1. Metadata de Oracle (sin sesión SQLite)
        meta = await self._meta_reader.leer_meta(suministro_id)
        if meta is None:
            logger.warning(
                "[PoblarSuministro] Sin metadata Oracle para %s — abortando", suministro_id
            )
            return

        logger.info(
            "[PoblarSuministro] %s → medidor=%s telemedible=%s",
            suministro_id,
            meta.medidor,
            meta.telemedible,
        )

        # 2. Coordenadas y tarifa en SQLite
        async with self._session_factory() as session:
            suministro_repo = SQLiteSuministroRepository(session)
            if meta.lat is not None and meta.lon is not None:
                await suministro_repo.upsert_coordenadas(suministro_id, meta.lat, meta.lon)
            else:
                await suministro_repo.crear_placeholder(suministro_id)
            if meta.codigo_tarifa:
                await suministro_repo.upsert_tarifa(suministro_id, meta.codigo_tarifa)
            await session.commit()

        # 3. Vecinos Oracle → vecinos_cache SQLite
        vecinos = await self._vecinos_repo.get_vecinos(suministro_id)
        async with self._session_factory() as session:
            vecinos_cache_repo = SQLiteVecinosCacheRepository(session)
            await vecinos_cache_repo.upsert(suministro_id, vecinos)
            await session.commit()
        logger.info("[PoblarSuministro] %d vecinos en caché para %s", len(vecinos), suministro_id)

        # 4. Sin medidor → no hay lecturas
        if not meta.medidor:
            logger.warning("[PoblarSuministro] Sin medidor para %s — sin lecturas", suministro_id)
            return

        # 4b. Verificar frescura: si hay datos de ayer o hoy, no re-ingestar
        async with self._session_factory() as session:
            ultima_fecha = await SQLiteConsumoDiarioRepository(session).get_ultima_fecha(
                suministro_id
            )

        if ultima_fecha is not None and (date.today() - ultima_fecha).days <= 1:
            logger.info(
                "[PoblarSuministro] Datos frescos para %s (ultimo: %s) — saltando ingesta",
                suministro_id,
                ultima_fecha,
            )
            return

        # 5. Estrategia según tipo de medidor
        strategy = self._selector.seleccionar(meta.telemedible)
        logger.info(
            "[PoblarSuministro] Usando estrategia %s para %s", strategy.nombre, suministro_id
        )

        desde = date.today() - timedelta(days=_DIAS_HISTORICO)
        hasta = date.today()
        lecturas = await strategy.leer_lecturas(meta.medidor, suministro_id, desde, hasta)
        logger.info(
            "[PoblarSuministro] %d lecturas obtenidas para %s", len(lecturas), suministro_id
        )

        if not lecturas:
            logger.info("[PoblarSuministro] Sin lecturas disponibles para %s", suministro_id)
            return

        # 6. Persistir via IngestarConsumoDiarioUseCase
        async with self._session_factory() as session:
            consumo_repo = SQLiteConsumoDiarioRepository(session)
            suministro_repo = SQLiteSuministroRepository(session)
            adapter = _LecturasAdapter(lecturas)
            resultado = await IngestarConsumoDiarioUseCase(
                adapter, consumo_repo, suministro_repo
            ).ejecutar(desde, hasta)
            await session.commit()

        logger.info(
            "[PoblarSuministro] Completado: %d días ingestados para %s",
            resultado.dias_procesados,
            suministro_id,
        )
