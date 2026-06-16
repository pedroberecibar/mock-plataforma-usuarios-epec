from datetime import date

from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository


async def test_get_vigente_returns_none_when_no_objetivo_was_set() -> None:
    repo = FakeObjetivoConsumoRepository()

    assert await repo.get_vigente("S1") is None


async def test_get_vigente_returns_the_most_recent_objetivo() -> None:
    repo = FakeObjetivoConsumoRepository()

    await repo.upsert_objetivo("S1", 150.0, "sugerido", date(2026, 1, 1))
    await repo.upsert_objetivo("S1", 180.0, "manual", date(2026, 3, 1))

    assert await repo.get_vigente("S1") == (180.0, "manual", date(2026, 3, 1))
