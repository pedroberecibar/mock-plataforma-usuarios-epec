from datetime import date, datetime

import pytest

from domain.ports.notificacion_config_repository import TIPOS_ALERTA
from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository


@pytest.fixture
def repo() -> FakeNotificacionConfigRepository:
    return FakeNotificacionConfigRepository()


async def test_get_config_devuelve_todos_los_tipos_deshabilitados_por_defecto(
    repo: FakeNotificacionConfigRepository,
) -> None:
    config = await repo.get_config("SRV-001")
    assert len(config) == len(TIPOS_ALERTA)
    assert all(not c.habilitado for c in config)


async def test_upsert_habilita_tipo(repo: FakeNotificacionConfigRepository) -> None:
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    config = await repo.get_config("SRV-001")
    tipos_habilitados = {c.tipo for c in config if c.habilitado}
    assert "factura_disponible" in tipos_habilitados


async def test_upsert_es_idempotente(repo: FakeNotificacionConfigRepository) -> None:
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    await repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    config = await repo.get_config("SRV-001")
    assert sum(1 for c in config if c.tipo == "factura_disponible") == 1


async def test_ya_enviada_hoy_devuelve_false_sin_registros(
    repo: FakeNotificacionConfigRepository,
) -> None:
    hoy = date(2026, 6, 18)
    assert not await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_ya_enviada_hoy_devuelve_true_tras_registrar(
    repo: FakeNotificacionConfigRepository,
) -> None:
    hoy = date(2026, 6, 18)
    await repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 18, 10, 0))
    assert await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_ya_enviada_hoy_distingue_por_dia(
    repo: FakeNotificacionConfigRepository,
) -> None:
    await repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 17, 10, 0))
    hoy = date(2026, 6, 18)
    assert not await repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_ya_enviada_hoy_distingue_por_suministro(
    repo: FakeNotificacionConfigRepository,
) -> None:
    hoy = date(2026, 6, 18)
    await repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 18, 10, 0))
    assert not await repo.ya_enviada_hoy("SRV-002", "factura_disponible", hoy)
