"""Tests TDD para CachedVecinosRepository.

Verifica:
- Cache miss: delega a inner y guarda en SQLite.
- Cache hit (fresco): devuelve SQLite sin llamar a inner.
- Cache expirado: llama a inner y actualiza SQLite.
- Inner falla: devuelve [] y no rompe el cache existente.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.ports.vecinos_repository import VecinosRepository
from infrastructure.sqlite.cached_vecinos_repository import CachedVecinosRepository
from infrastructure.sqlite.models import Base


class _FakeVecinosRepository(VecinosRepository):
    def __init__(self, vecinos: list[str], *, fail: bool = False) -> None:
        self._vecinos = vecinos
        self._fail = fail
        self.call_count = 0

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        self.call_count += 1
        if self._fail:
            raise RuntimeError("Oracle error")
        return self._vecinos

    async def get_equipos_activos(self, suministro_ids: list[str]) -> list[str]:
        return []


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


async def test_cache_miss_llama_inner_y_devuelve_vecinos(session: AsyncSession) -> None:
    inner = _FakeVecinosRepository(["V1", "V2", "V3"])
    repo = CachedVecinosRepository(inner, session)

    result = await repo.get_vecinos("S1")

    assert result == ["V1", "V2", "V3"]
    assert inner.call_count == 1


async def test_cache_miss_guarda_resultado_en_sqlite(session: AsyncSession) -> None:
    inner = _FakeVecinosRepository(["V1", "V2"])
    repo = CachedVecinosRepository(inner, session)

    await repo.get_vecinos("S1")
    # Segunda llamada debe usar cache — inner no se llama de nuevo
    result = await repo.get_vecinos("S1")

    assert result == ["V1", "V2"]
    assert inner.call_count == 1  # inner solo fue llamado una vez


async def test_cache_hit_fresco_no_llama_inner(session: AsyncSession) -> None:
    inner = _FakeVecinosRepository(["V1"])
    repo = CachedVecinosRepository(inner, session)

    await repo.get_vecinos("S1")
    await repo.get_vecinos("S1")
    await repo.get_vecinos("S1")

    assert inner.call_count == 1


async def test_cache_expirado_refresca_desde_inner(session: AsyncSession) -> None:
    inner = _FakeVecinosRepository(["V1"])
    repo = CachedVecinosRepository(inner, session, ttl_hours=0)  # TTL 0 → siempre expirado

    await repo.get_vecinos("S1")
    await repo.get_vecinos("S1")

    assert inner.call_count == 2


async def test_inner_falla_devuelve_lista_vacia(session: AsyncSession) -> None:
    inner = _FakeVecinosRepository([], fail=True)
    repo = CachedVecinosRepository(inner, session)

    result = await repo.get_vecinos("S1")

    assert result == []


async def test_suministros_distintos_tienen_cache_independiente(session: AsyncSession) -> None:
    inner_s1 = _FakeVecinosRepository(["V1", "V2"])
    inner_s2 = _FakeVecinosRepository(["V3"])

    # Two repo instances share the same session but different inners
    repo1 = CachedVecinosRepository(inner_s1, session)
    repo2 = CachedVecinosRepository(inner_s2, session)

    r1 = await repo1.get_vecinos("S1")
    r2 = await repo2.get_vecinos("S2")

    assert r1 == ["V1", "V2"]
    assert r2 == ["V3"]
