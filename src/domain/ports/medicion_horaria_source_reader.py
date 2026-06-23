from abc import ABC, abstractmethod
from datetime import date

from domain.lecturas_horarias import LecturaHoraria


class MedicionHorariaSourceReader(ABC):
    @abstractmethod
    async def leer_lecturas_horarias(
        self, desde: date, hasta: date, equipos: list[str] | None = None
    ) -> list[LecturaHoraria]:
        """Devuelve lecturas horarias en [desde, hasta].
        Si `equipos` se provee, filtra solo esos med_numero_equipo; None = todos."""
