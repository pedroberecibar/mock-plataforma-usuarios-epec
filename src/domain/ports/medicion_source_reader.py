from abc import ABC, abstractmethod
from datetime import date

from domain.lecturas import LecturaTelemedida


class MedicionSourceReader(ABC):
    @abstractmethod
    async def leer_lecturas(self, desde: date, hasta: date) -> list[LecturaTelemedida]:
        """Devuelve lecturas en [desde, hasta] más la última lectura anterior a `desde`
        por equipo (ancla), necesaria para calcular el delta en ventanas incrementales."""
