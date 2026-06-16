from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> SQLiteConsumoDiarioRepository:
    return SQLiteConsumoDiarioRepository(db_session)


async def test_upsert_persiste_y_get_serie_recupera(
    repo: SQLiteConsumoDiarioRepository,
    suministro_fixture: str,
) -> None:
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 10.5)

    serie = await repo.get_serie(suministro_fixture, date(2026, 6, 1), date(2026, 6, 30))

    assert serie == [(date(2026, 6, 1), 10.5)]


async def test_get_serie_filtra_por_rango_de_fechas(
    repo: SQLiteConsumoDiarioRepository,
    suministro_fixture: str,
) -> None:
    await repo.upsert_consumo(suministro_fixture, date(2026, 5, 31), 5.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 10.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 30), 12.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 7, 1), 99.0)

    serie = await repo.get_serie(suministro_fixture, date(2026, 6, 1), date(2026, 6, 30))

    fechas = [f for f, _ in serie]
    assert date(2026, 5, 31) not in fechas
    assert date(2026, 7, 1) not in fechas
    assert date(2026, 6, 1) in fechas
    assert date(2026, 6, 30) in fechas


async def test_get_serie_devuelve_ordenado_por_fecha(
    repo: SQLiteConsumoDiarioRepository,
    suministro_fixture: str,
) -> None:
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 3), 3.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 1.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 2), 2.0)

    serie = await repo.get_serie(suministro_fixture, date(2026, 6, 1), date(2026, 6, 30))

    fechas = [f for f, _ in serie]
    assert fechas == sorted(fechas)


async def test_get_serie_aisla_por_suministro(
    db_session: AsyncSession,
    suministro_fixture: str,
) -> None:
    from infrastructure.sqlite.models import Suministro

    db_session.add(Suministro(id="S-OTRO", lat=0.0, lon=0.0, suministro_referencia="99"))
    await db_session.flush()

    repo = SQLiteConsumoDiarioRepository(db_session)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S-OTRO", date(2026, 6, 1), 999.0)

    serie = await repo.get_serie(suministro_fixture, date(2026, 6, 1), date(2026, 6, 30))

    assert all(kwh != 999.0 for _, kwh in serie)


async def test_upsert_es_idempotente(
    repo: SQLiteConsumoDiarioRepository,
    suministro_fixture: str,
) -> None:
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 10.0)
    await repo.upsert_consumo(suministro_fixture, date(2026, 6, 1), 20.0)

    serie = await repo.get_serie(suministro_fixture, date(2026, 6, 1), date(2026, 6, 1))

    assert serie == [(date(2026, 6, 1), 20.0)]
