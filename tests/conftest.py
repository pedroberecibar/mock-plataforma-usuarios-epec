"""conftest.py — Shared pytest fixtures for the entire test suite."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, Suministro


@pytest.fixture
async def db_session_factory() -> async_sessionmaker[AsyncSession]:
    """Session factory respaldada por SQLite in-memory. Para use cases con BackgroundTask."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    yield factory
    await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncSession:
    """Fresh in-memory SQLite per test — garantiza aislamiento total entre tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def suministro_fixture(db_session: AsyncSession) -> str:
    """Inserta un Suministro de prueba y devuelve su id (requerido por FK de consumo_diario)."""
    sid = "S-TEST-001"
    db_session.add(Suministro(id=sid, lat=-31.42, lon=-64.18, suministro_referencia="91013496"))
    await db_session.flush()
    return sid
