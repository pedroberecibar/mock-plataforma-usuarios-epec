import pytest

from domain.ports.usuario_repository import UsuarioRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        UsuarioRepository()  # type: ignore[abstract]


def test_declares_abstract_methods() -> None:
    assert UsuarioRepository.__abstractmethods__ == frozenset(
        {"get_suministro_id", "get_password_hash", "get_email"}
    )
