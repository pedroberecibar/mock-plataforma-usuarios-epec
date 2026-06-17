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


async def test_get_ultima_fecha_devuelve_la_fecha_maxima() -> None:
    repo = FakeConsumoDiarioRepository()

    await repo.upsert_consumo("S1", date(2026, 6, 10), 5.0)
    await repo.upsert_consumo("S1", date(2026, 6, 5), 3.0)
    await repo.upsert_consumo("S1", date(2026, 6, 15), 8.0)

    result = await repo.get_ultima_fecha("S1")

    assert result == date(2026, 6, 15)


async def test_get_ultima_fecha_devuelve_none_si_no_hay_datos() -> None:
    repo = FakeConsumoDiarioRepository()

    result = await repo.get_ultima_fecha("S1")

    assert result is None


async def test_get_ultima_fecha_aislado_por_suministro() -> None:
    repo = FakeConsumoDiarioRepository()

    await repo.upsert_consumo("S1", date(2026, 6, 1), 5.0)
    await repo.upsert_consumo("S2", date(2026, 6, 20), 99.0)

    assert await repo.get_ultima_fecha("S1") == date(2026, 6, 1)
    assert await repo.get_ultima_fecha("S2") == date(2026, 6, 20)
