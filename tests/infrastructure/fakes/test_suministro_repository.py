from infrastructure.fakes.suministro_repository import FakeSuministroRepository


async def test_existe_devuelve_false_para_suministro_inexistente() -> None:
    repo = FakeSuministroRepository()
    assert not await repo.existe("SRV-001")


async def test_crear_placeholder_permite_existencia() -> None:
    repo = FakeSuministroRepository()
    await repo.crear_placeholder("SRV-001")
    assert await repo.existe("SRV-001")


async def test_crear_placeholder_es_idempotente() -> None:
    repo = FakeSuministroRepository()
    await repo.crear_placeholder("SRV-001")
    await repo.crear_placeholder("SRV-001")
    assert await repo.existe("SRV-001")
