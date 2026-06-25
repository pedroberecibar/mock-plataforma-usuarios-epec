from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.oracle.strategies._sigec_base import SigecBaseStrategy


class ChupeteIngestionStrategy(SigecBaseStrategy, SuministroIngestionStrategy):
    """Estrategia de ingesta para medidores sin AMI (lecturas manuales / chupete).

    Lee de XXCO_LECTURAS_TELEMEDIDAS: si hay lecturas manuales en SIGEC las ingesta;
    si no, retorna lista vacía sin error.
    """

    @property
    def nombre(self) -> str:
        return "CHUPETE"
