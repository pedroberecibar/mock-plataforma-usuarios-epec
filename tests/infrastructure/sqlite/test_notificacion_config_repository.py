from datetime import date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.notificacion_config_repository import TIPOS_ALERTA
from infrastructure.sqlite.notificacion_config_repository import SQLiteNotificacionConfigRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> SQLiteNotificacionConfigRepository:
    return SQLiteNotificacionConfigRepository(db_session)


async def test_get_config_devuelve_todos_los_tipos_por_defecto(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    config = await repo.get_config("SRV-001")
    assert len(config) == len(TIPOS_ALERTA)
    assert all(not c.habilitado for c in config)


async def test_upsert_persiste_habilitado(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    config = await repo.get_config("SRV-001")
    tipos = {c.tipo: c.habilitado for c in config}
    assert tipos["factura_disponible"] is True
    assert tipos["vencimiento_proximo"] is False


async def test_upsert_actualiza_valor_existente(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=False)
    config = await repo.get_config("SRV-001")
    tipos = {c.tipo: c.habilitado for c in config}
    assert tipos["factura_disponible"] is False


async def test_ya_enviada_hoy_false_sin_registros(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    hoy = date(2026, 6, 18)
    assert not await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_ya_enviada_hoy_true_tras_registrar(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    hoy = date(2026, 6, 18)
    await repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 18, 9, 0))
    assert await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_ya_enviada_hoy_false_para_dia_distinto(
    repo: SQLiteNotificacionConfigRepository,
) -> None:
    await repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 17, 9, 0))
    hoy = date(2026, 6, 18)
    assert not await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)
