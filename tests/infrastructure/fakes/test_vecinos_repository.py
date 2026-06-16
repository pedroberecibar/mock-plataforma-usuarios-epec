from infrastructure.fakes.vecinos_repository import FakeVecinosRepository


async def test_returns_the_preconfigured_vecinos_for_a_suministro() -> None:
    repo = FakeVecinosRepository(vecinos={"S1": ["S2", "S3"]})

    assert await repo.get_vecinos("S1", 150.0) == ["S2", "S3"]


async def test_returns_empty_list_when_suministro_has_no_vecinos_configured() -> None:
    repo = FakeVecinosRepository()

    assert await repo.get_vecinos("S1", 150.0) == []
