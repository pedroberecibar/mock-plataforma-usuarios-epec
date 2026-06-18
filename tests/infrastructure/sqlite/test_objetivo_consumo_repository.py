from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, Suministro
from infrastructure.sqlite.objetivo_consumo_repository import SQLiteObjetivoConsumoRepository


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        s.add(Suministro(id="S1", lat=0.0, lon=0.0, suministro_referencia="REF"))
        await s.commit()
        yield s
    await engine.dispose()


async def test_get_vigente_returns_none_when_empty(session: AsyncSession) -> None:
    repo = SQLiteObjetivoConsumoRepository(session)
    assert await repo.get_vigente("S1") is None


async def test_upsert_y_get_vigente(session: AsyncSession) -> None:
    repo = SQLiteObjetivoConsumoRepository(session)
    await repo.upsert_objetivo("S1", 150.0, "manual", date(2026, 6, 1))

    resultado = await repo.get_vigente("S1")

    assert resultado is not None
    valor, origen, vigente_desde = resultado
    assert valor == 150.0
    assert origen == "manual"
    assert vigente_desde == date(2026, 6, 1)


async def test_get_vigente_devuelve_el_mas_reciente(session: AsyncSession) -> None:
    repo = SQLiteObjetivoConsumoRepository(session)
    await repo.upsert_objetivo("S1", 100.0, "manual", date(2026, 1, 1))
    await repo.upsert_objetivo("S1", 200.0, "manual", date(2026, 6, 1))

    resultado = await repo.get_vigente("S1")

    assert resultado is not None
    assert resultado[0] == 200.0


async def test_upsert_actualiza_valor_existente_en_misma_fecha(session: AsyncSession) -> None:
    repo = SQLiteObjetivoConsumoRepository(session)
    hoy = date(2026, 6, 18)
    await repo.upsert_objetivo("S1", 100.0, "manual", hoy)
    await repo.upsert_objetivo("S1", 180.0, "manual", hoy)

    resultado = await repo.get_vigente("S1")
    assert resultado is not None
    assert resultado[0] == 180.0
