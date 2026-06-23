import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.models import Suministro
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> SQLiteSuministroRepository:
    return SQLiteSuministroRepository(db_session)


async def test_existe_devuelve_false_para_suministro_inexistente(
    repo: SQLiteSuministroRepository,
) -> None:
    assert not await repo.existe("SRV-999")


async def test_crear_placeholder_persiste_suministro(
    repo: SQLiteSuministroRepository,
) -> None:
    await repo.crear_placeholder("SRV-001")
    assert await repo.existe("SRV-001")


async def test_crear_placeholder_usa_ceros_como_coordenadas(
    repo: SQLiteSuministroRepository,
    db_session: AsyncSession,
) -> None:
    await repo.crear_placeholder("SRV-001")
    result = await db_session.execute(select(Suministro).where(Suministro.id == "SRV-001"))
    row = result.scalar_one()
    assert row.lat == 0.0
    assert row.lon == 0.0
    assert row.suministro_referencia == "SRV-001"


async def test_crear_placeholder_es_idempotente(
    repo: SQLiteSuministroRepository,
) -> None:
    await repo.crear_placeholder("SRV-001")
    await repo.crear_placeholder("SRV-001")
    assert await repo.existe("SRV-001")


async def test_upsert_coordenadas_crea_suministro_si_no_existe(
    repo: SQLiteSuministroRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert_coordenadas("SRV-NEW", -31.45, -64.14)
    result = await db_session.execute(select(Suministro).where(Suministro.id == "SRV-NEW"))
    row = result.scalar_one()
    assert row.lat == -31.45
    assert row.lon == -64.14


async def test_upsert_coordenadas_actualiza_placeholder_con_ceros(
    repo: SQLiteSuministroRepository,
    db_session: AsyncSession,
) -> None:
    await repo.crear_placeholder("SRV-001")
    await repo.upsert_coordenadas("SRV-001", -31.45, -64.14)
    result = await db_session.execute(select(Suministro).where(Suministro.id == "SRV-001"))
    row = result.scalar_one()
    assert row.lat == -31.45
    assert row.lon == -64.14


async def test_upsert_coordenadas_es_idempotente(
    repo: SQLiteSuministroRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert_coordenadas("SRV-001", -31.45, -64.14)
    await repo.upsert_coordenadas("SRV-001", -31.45, -64.14)
    result = await db_session.execute(select(Suministro).where(Suministro.id == "SRV-001"))
    assert result.scalar_one().lat == -31.45


async def test_crear_placeholder_no_pisa_coordenadas_reales(
    repo: SQLiteSuministroRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert_coordenadas("SRV-001", -31.45, -64.14)
    await repo.crear_placeholder("SRV-001")  # ON CONFLICT DO NOTHING → no debe pisar
    result = await db_session.execute(select(Suministro).where(Suministro.id == "SRV-001"))
    row = result.scalar_one()
    assert row.lat == -31.45  # coordenadas reales intactas
