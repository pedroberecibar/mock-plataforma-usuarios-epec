"""Tests para SQLiteVecinosCacheRepository."""

import json

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.vecinos_cache_repository import SQLiteVecinosCacheRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> SQLiteVecinosCacheRepository:
    return SQLiteVecinosCacheRepository(db_session)


async def test_upsert_inserta_vecinos_nuevos(
    repo: SQLiteVecinosCacheRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert("SRV-100", ["SRV-200", "SRV-300"])
    result = await db_session.execute(
        text("SELECT vecinos_json FROM vecinos_cache WHERE suministro_id = 'SRV-100'")
    )
    row = result.fetchone()
    assert row is not None
    assert set(json.loads(row[0])) == {"SRV-200", "SRV-300"}


async def test_upsert_actualiza_vecinos_existentes(
    repo: SQLiteVecinosCacheRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert("SRV-100", ["SRV-200"])
    await repo.upsert("SRV-100", ["SRV-300", "SRV-400"])
    result = await db_session.execute(
        text("SELECT vecinos_json FROM vecinos_cache WHERE suministro_id = 'SRV-100'")
    )
    row = result.fetchone()
    assert set(json.loads(row[0])) == {"SRV-300", "SRV-400"}


async def test_upsert_lista_vacia(
    repo: SQLiteVecinosCacheRepository,
    db_session: AsyncSession,
) -> None:
    await repo.upsert("SRV-100", [])
    result = await db_session.execute(
        text("SELECT vecinos_json FROM vecinos_cache WHERE suministro_id = 'SRV-100'")
    )
    row = result.fetchone()
    assert json.loads(row[0]) == []
