from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.oracle.strategies._sigec_base import SigecBaseStrategy


class ClouIngestionStrategy(SigecBaseStrategy, SuministroIngestionStrategy):
    """Estrategia de ingesta para medidores CLOU.

    Hoy lee de XXCO_LECTURAS_TELEMEDIDAS (SIGEC).
    TODO: migrar a SHENYU1 (AMI CLOU) cuando los perfiles 15-min sean accesibles.
    """

    @property
    def nombre(self) -> str:
        return "CLOU"

    @property
    def soporta_perfiles(self) -> bool:
        return True
