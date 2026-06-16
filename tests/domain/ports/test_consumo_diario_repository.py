import pytest

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ConsumoDiarioRepository()  # type: ignore[abstract]


def test_declares_get_serie_and_upsert_consumo_as_abstract() -> None:
    assert ConsumoDiarioRepository.__abstractmethods__ == frozenset({"get_serie", "upsert_consumo"})
