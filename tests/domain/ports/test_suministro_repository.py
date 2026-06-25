import pytest

from domain.ports.suministro_repository import SuministroRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        SuministroRepository()  # type: ignore[abstract]


def test_declares_abstract_methods() -> None:
    assert SuministroRepository.__abstractmethods__ == frozenset(
        {"existe", "crear_placeholder", "upsert_coordenadas", "get_tarifa_codigo", "upsert_tarifa"}
    )
