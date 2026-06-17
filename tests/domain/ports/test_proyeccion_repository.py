import pytest

from domain.ports.proyeccion_repository import ProyeccionRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ProyeccionRepository()  # type: ignore[abstract]


def test_declares_expected_abstract_methods() -> None:
    assert ProyeccionRepository.__abstractmethods__ == frozenset(
        {"get_proyeccion", "upsert_proyeccion"}
    )
