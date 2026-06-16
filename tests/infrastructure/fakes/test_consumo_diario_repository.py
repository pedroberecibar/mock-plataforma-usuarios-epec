from datetime import date

from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository


async def test_upsert_then_get_serie_returns_only_the_requested_suministro_and_range() -> None:
    repo = FakeConsumoDiarioRepository()

    await repo.upsert_consumo("S1", date(2026, 1, 1), 10.0)
    await repo.upsert_consumo("S1", date(2026, 1, 2), 12.0)
    await repo.upsert_consumo("S1", date(2026, 1, 10), 99.0)
    await repo.upsert_consumo("S2", date(2026, 1, 1), 5.0)

    serie = await repo.get_serie("S1", date(2026, 1, 1), date(2026, 1, 2))

    assert serie == [(date(2026, 1, 1), 10.0), (date(2026, 1, 2), 12.0)]


async def test_upsert_overwrites_the_value_for_the_same_day() -> None:
    repo = FakeConsumoDiarioRepository()

    await repo.upsert_consumo("S1", date(2026, 1, 1), 10.0)
    await repo.upsert_consumo("S1", date(2026, 1, 1), 20.0)

    serie = await repo.get_serie("S1", date(2026, 1, 1), date(2026, 1, 1))

    assert serie == [(date(2026, 1, 1), 20.0)]
