from abc import ABC, abstractmethod
from datetime import date

ORIGEN_OBJETIVO = ("sugerido", "manual")


class ObjetivoConsumoRepository(ABC):
    @abstractmethod
    async def get_vigente(self, suministro_id: str) -> tuple[float, str, date] | None:
        """Devuelve (valor_kwh, origen, vigente_desde) del objetivo vigente, o None."""

    @abstractmethod
    async def upsert_objetivo(
        self, suministro_id: str, valor_kwh: float, origen: str, vigente_desde: date
    ) -> None:
        """Inserta o actualiza el objetivo de consumo vigente de un suministro."""
