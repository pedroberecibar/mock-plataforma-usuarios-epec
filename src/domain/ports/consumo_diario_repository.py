from abc import ABC, abstractmethod
from datetime import date


class ConsumoDiarioRepository(ABC):
    @abstractmethod
    async def get_serie(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, float]]:
        """Devuelve la serie de consumo diario (fecha, kWh) en el rango dado."""

    @abstractmethod
    async def upsert_consumo(self, suministro_id: str, fecha: date, kwh: float) -> None:
        """Inserta o actualiza el consumo de un día para un suministro."""

    @abstractmethod
    async def get_ultima_fecha(self, suministro_id: str) -> date | None:
        """Última fecha con dato disponible para el suministro; None si no hay datos."""
