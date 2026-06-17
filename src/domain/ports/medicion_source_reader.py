from abc import ABC, abstractmethod
from datetime import date

from domain.lecturas import LecturaTelemedida


class MedicionSourceReader(ABC):
    @abstractmethod
    async def leer_lecturas(
        self,
        desde: date,
        hasta: date,
        equipos: list[str] | None = None,
    ) -> list[LecturaTelemedida]:
        """Devuelve lecturas en [desde, hasta].
        Si `equipos` se provee, filtra solo esos med_numero_equipo; None = todos."""
