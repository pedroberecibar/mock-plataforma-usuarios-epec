from abc import ABC, abstractmethod
from datetime import date

from domain.lecturas import LecturaTelemedida


class SuministroIngestionStrategy(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str: ...

    @abstractmethod
    async def leer_lecturas(
        self,
        medidor: str,
        srv_codigo: str,
        desde: date,
        hasta: date,
    ) -> list[LecturaTelemedida]: ...
