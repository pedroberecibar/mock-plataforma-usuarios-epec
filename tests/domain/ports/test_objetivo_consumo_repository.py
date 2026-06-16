import pytest

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ObjetivoConsumoRepository()  # type: ignore[abstract]


def test_declares_get_vigente_and_upsert_objetivo_as_abstract() -> None:
    assert ObjetivoConsumoRepository.__abstractmethods__ == frozenset(
        {"get_vigente", "upsert_objetivo"}
    )
