import pytest

from domain.ports.auth_provider import AuthProvider


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        AuthProvider()  # type: ignore[abstract]


def test_declares_autenticar_verificar_token_and_verificar_password_as_abstract() -> None:
    assert AuthProvider.__abstractmethods__ == frozenset(
        {"autenticar", "verificar_token", "verificar_password"}
    )
