import pytest

from domain.ports.vecinos_repository import VecinosRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        VecinosRepository()  # type: ignore[abstract]


def test_declares_get_vecinos_as_abstract() -> None:
    assert VecinosRepository.__abstractmethods__ == frozenset(
        {"get_vecinos", "get_equipos_activos"}
    )
