import pytest

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ConsumoDiarioRepository()  # type: ignore[abstract]


def test_declares_abstract_methods() -> None:
    assert ConsumoDiarioRepository.__abstractmethods__ == frozenset(
        {
            "get_serie",
            "upsert_consumo",
            "get_ultima_fecha",
            "get_serie_promedio_zona",
            "get_totales_por_suministro",
        }
    )
