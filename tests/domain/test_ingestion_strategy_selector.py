"""Tests para IngestionStrategySelector — sin I/O."""

import pytest

from infrastructure.oracle.ingestion_strategy_selector import IngestionStrategySelector
from infrastructure.oracle.strategies.chupete_strategy import ChupeteIngestionStrategy
from infrastructure.oracle.strategies.clou_strategy import ClouIngestionStrategy
from infrastructure.oracle.strategies.nansen_strategy import NansenIngestionStrategy


@pytest.fixture
def selector() -> IngestionStrategySelector:
    # Las estrategias no se conectan a Oracle en __init__ si no hay env vars.
    # Usamos subclases anónimas que no llaman super().__init__ para evitar dep de env.
    class _FakeClou(ClouIngestionStrategy):
        def __init__(self) -> None:
            pass  # skip Oracle init

    class _FakeNansen(NansenIngestionStrategy):
        def __init__(self) -> None:
            pass

    class _FakeChupete(ChupeteIngestionStrategy):
        def __init__(self) -> None:
            pass

    return IngestionStrategySelector(
        clou=_FakeClou(),
        nansen=_FakeNansen(),
        chupete=_FakeChupete(),
    )


def test_selecciona_clou_para_telemedible_clou(selector: IngestionStrategySelector) -> None:
    s = selector.seleccionar("CLOU")
    assert s.nombre == "CLOU"


def test_selecciona_clou_case_insensitive(selector: IngestionStrategySelector) -> None:
    s = selector.seleccionar("clou")
    assert s.nombre == "CLOU"


def test_selecciona_nansen_para_telemedible_nansen(selector: IngestionStrategySelector) -> None:
    s = selector.seleccionar("NANSEN")
    assert s.nombre == "NANSEN"


def test_selecciona_chupete_para_telemedible_desconocido(
    selector: IngestionStrategySelector,
) -> None:
    s = selector.seleccionar("OTRO")
    assert s.nombre == "CHUPETE"


def test_selecciona_chupete_para_telemedible_none(selector: IngestionStrategySelector) -> None:
    s = selector.seleccionar(None)
    assert s.nombre == "CHUPETE"


def test_selecciona_chupete_para_cadena_vacia(selector: IngestionStrategySelector) -> None:
    s = selector.seleccionar("")
    assert s.nombre == "CHUPETE"
