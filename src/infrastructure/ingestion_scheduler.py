"""Scheduler de ingesta periódica Oracle → SQLite.

Corre como una tarea asyncio en background (ver main.py).
Hace un backfill inicial al arrancar y luego loops cada INGEST_INTERVAL_HORAS.

OracleMedicionReader usa oracledb síncrono. _NonBlockingReader lo envuelve
ejecutando leer_lecturas() en un thread pool para no bloquear el event loop.
"""

import asyncio
import logging
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase
from domain.lecturas import LecturaTelemedida
from domain.ports.medicion_source_reader import MedicionSourceReader
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository

_log = logging.getLogger(__name__)


class _NonBlockingReader(MedicionSourceReader):
    """Wrapper que ejecuta leer_lecturas() del delegate en un thread pool.

    Evita que el call síncrono de oracledb bloquee el event loop de asyncio.
    """

    def __init__(self, delegate: MedicionSourceReader) -> None:
        self._delegate = delegate

    async def leer_lecturas(self, desde: date, hasta: date) -> list[LecturaTelemedida]:
        loop = asyncio.get_running_loop()

        def _sync() -> list[LecturaTelemedida]:
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(self._delegate.leer_lecturas(desde, hasta))
            finally:
                new_loop.close()

        return await loop.run_in_executor(None, _sync)


async def _ejecutar_ingesta(
    reader: MedicionSourceReader,
    session_factory: async_sessionmaker[AsyncSession],
    desde: date,
    hasta: date,
) -> None:
    async with session_factory() as session:
        consumo_repo = SQLiteConsumoDiarioRepository(session)
        suministro_repo = SQLiteSuministroRepository(session)
        resultado = await IngestarConsumoDiarioUseCase(
            reader, consumo_repo, suministro_repo
        ).ejecutar(desde, hasta)
        await session.commit()
    _log.info(
        "Ingesta OK — %d suministros, %d días (desde=%s hasta=%s)",
        resultado.suministros_procesados,
        resultado.dias_procesados,
        desde,
        hasta,
    )


async def run_scheduler(
    reader: MedicionSourceReader,
    session_factory: async_sessionmaker[AsyncSession],
    *,
    desde_inicial: date,
    lookback_dias: int,
    interval_horas: int,
) -> None:
    """Backfill inicial + loop periódico. Diseñado para cancelarse limpiamente con asyncio.

    Procesa de a 1 día para evitar fetchall de millones de filas (EPEC tiene ~380K lecturas/día).
    """
    non_blocking = _NonBlockingReader(reader)

    _log.info(
        "Scheduler iniciado — backfill desde %s, intervalo %dh", desde_inicial, interval_horas
    )

    # Backfill: ventanas de 2 días (D, D+1) para que _persistir_serie tenga la lectura
    # siguiente sin necesidad de una query ANCLAS separada en Oracle.
    hoy = date.today()
    dia = desde_inicial
    while dia <= hoy:
        hasta = dia + timedelta(days=1)  # D+1 actúa como lectura siguiente para D
        try:
            await _ejecutar_ingesta(non_blocking, session_factory, dia, hasta)
        except asyncio.CancelledError:
            _log.info("Scheduler detenido durante backfill.")
            return
        except Exception:
            _log.exception("Error en backfill %s — continuando con el siguiente día", dia)
        dia += timedelta(days=1)

    while True:
        try:
            await asyncio.sleep(interval_horas * 3600)
        except asyncio.CancelledError:
            _log.info("Scheduler detenido.")
            return

        hoy = date.today()
        dia = hoy - timedelta(days=lookback_dias)
        while dia <= hoy:
            hasta = dia + timedelta(days=1)
            try:
                await _ejecutar_ingesta(non_blocking, session_factory, dia, hasta)
            except asyncio.CancelledError:
                _log.info("Scheduler detenido durante ingesta periódica.")
                return
            except Exception:
                _log.exception("Error en ingesta %s — reintentará en %dh", dia, interval_horas)
            dia += timedelta(days=1)
