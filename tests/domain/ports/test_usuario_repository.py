import pytest

from domain.ports.usuario_repository import UsuarioRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        UsuarioRepository()  # type: ignore[abstract]


def test_declares_get_suministro_id_and_get_password_hash_as_abstract() -> None:
    assert UsuarioRepository.__abstractmethods__ == frozenset(
        {"get_suministro_id", "get_password_hash"}
    )
