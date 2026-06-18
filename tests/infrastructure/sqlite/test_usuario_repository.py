import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.models import Usuario
from infrastructure.sqlite.usuario_repository import SQLiteUsuarioRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> SQLiteUsuarioRepository:
    return SQLiteUsuarioRepository(db_session)


async def test_devuelve_none_para_usuario_inexistente(
    repo: SQLiteUsuarioRepository,
) -> None:
    assert await repo.get_suministro_id("nadie") is None


async def test_devuelve_suministro_id_para_usuario_existente(
    repo: SQLiteUsuarioRepository,
    db_session: AsyncSession,
) -> None:
    db_session.add(Usuario(usuario="demo", suministro_id="3037481"))
    await db_session.flush()

    assert await repo.get_suministro_id("demo") == "3037481"


async def test_distingue_entre_usuarios_distintos(
    repo: SQLiteUsuarioRepository,
    db_session: AsyncSession,
) -> None:
    db_session.add(Usuario(usuario="pedro", suministro_id="1111111"))
    db_session.add(Usuario(usuario="maria", suministro_id="2222222"))
    await db_session.flush()

    assert await repo.get_suministro_id("pedro") == "1111111"
    assert await repo.get_suministro_id("maria") == "2222222"
