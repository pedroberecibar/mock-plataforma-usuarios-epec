from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.oracle.strategies._sigec_base import SigecBaseStrategy


class NansenIngestionStrategy(SigecBaseStrategy, SuministroIngestionStrategy):
    """Estrategia de ingesta para medidores NANSEN.

    Hoy lee de XXCO_LECTURAS_TELEMEDIDAS (SIGEC).
    TODO: migrar a tablas AMI NANSEN cuando los perfiles 15-min sean accesibles.
    """

    @property
    def nombre(self) -> str:
        return "NANSEN"
