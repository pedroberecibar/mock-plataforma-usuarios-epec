from abc import ABC, abstractmethod
from datetime import date


class ConsumoHorarioRepository(ABC):
    @abstractmethod
    async def get_serie_horaria(self, suministro_id: str, fecha: date) -> list[tuple[int, float]]:
        """Retorna [(hora 0-23, kWh), ...] para el día dado, ordenado por hora."""

    @abstractmethod
    async def upsert_consumo_horario(
        self, suministro_id: str, fecha: date, hora: int, kwh: float
    ) -> None:
        """Inserta o actualiza el consumo de una hora para un suministro."""

    @abstractmethod
    async def get_ultima_fecha_horaria(self, suministro_id: str) -> date | None:
        """Última fecha con datos horarios disponibles; None si no hay datos."""

    @abstractmethod
    async def get_serie_horaria_rango(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, int, float]]:
        """Retorna [(fecha, hora, kWh), ...] en el rango dado, ordenado por (fecha, hora)."""
