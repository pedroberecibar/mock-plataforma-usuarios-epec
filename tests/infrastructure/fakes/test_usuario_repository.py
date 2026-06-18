import pytest

from infrastructure.fakes.usuario_repository import FakeUsuarioRepository


@pytest.fixture
def repo() -> FakeUsuarioRepository:
    return FakeUsuarioRepository({"demo": "3037481", "otro": "9999999"})


async def test_devuelve_suministro_id_para_usuario_conocido(
    repo: FakeUsuarioRepository,
) -> None:
    assert await repo.get_suministro_id("demo") == "3037481"


async def test_devuelve_none_para_usuario_desconocido(
    repo: FakeUsuarioRepository,
) -> None:
    assert await repo.get_suministro_id("inexistente") is None


async def test_repo_vacio_devuelve_none_siempre() -> None:
    repo = FakeUsuarioRepository()
    assert await repo.get_suministro_id("cualquiera") is None


async def test_get_email_devuelve_email_cuando_existe() -> None:
    repo = FakeUsuarioRepository(emails={"demo": "demo@example.com"})
    assert await repo.get_email("demo") == "demo@example.com"


async def test_get_email_devuelve_none_para_usuario_sin_email() -> None:
    repo = FakeUsuarioRepository({"demo": "3037481"})
    assert await repo.get_email("demo") is None
