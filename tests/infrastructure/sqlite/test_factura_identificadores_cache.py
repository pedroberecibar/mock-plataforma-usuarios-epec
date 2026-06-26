from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.factura_identificadores import FacturaIdentificadores
from infrastructure.sqlite.factura_identificadores_cache import (
    SQLiteFacturaIdentificadoresCache,
)

IDS = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")


async def test_get_devuelve_none_si_no_hay_registro(db_session: AsyncSession) -> None:
    cache = SQLiteFacturaIdentificadoresCache(db_session)
    assert await cache.get("SRV-2817670") is None


async def test_guardar_y_recuperar(db_session: AsyncSession) -> None:
    cache = SQLiteFacturaIdentificadoresCache(db_session)
    await cache.guardar("SRV-2817670", IDS)
    assert await cache.get("SRV-2817670") == IDS


async def test_guardar_es_idempotente_por_suministro(db_session: AsyncSession) -> None:
    cache = SQLiteFacturaIdentificadoresCache(db_session)
    await cache.guardar("SRV-2817670", IDS)
    nuevos = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767099")
    await cache.guardar("SRV-2817670", nuevos)
    assert await cache.get("SRV-2817670") == nuevos
