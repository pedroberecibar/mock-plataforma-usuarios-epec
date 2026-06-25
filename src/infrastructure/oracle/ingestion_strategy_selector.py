from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.oracle.strategies.chupete_strategy import ChupeteIngestionStrategy
from infrastructure.oracle.strategies.clou_strategy import ClouIngestionStrategy
from infrastructure.oracle.strategies.nansen_strategy import NansenIngestionStrategy


class IngestionStrategySelector:
    def __init__(
        self,
        clou: ClouIngestionStrategy,
        nansen: NansenIngestionStrategy,
        chupete: ChupeteIngestionStrategy,
    ) -> None:
        self._clou = clou
        self._nansen = nansen
        self._chupete = chupete

    def seleccionar(self, telemedible: str | None) -> SuministroIngestionStrategy:
        match (telemedible or "").upper():
            case "CLOU":
                return self._clou
            case "NANSEN":
                return self._nansen
            case _:
                return self._chupete
