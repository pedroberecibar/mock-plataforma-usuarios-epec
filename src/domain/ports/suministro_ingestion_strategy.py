from abc import ABC, abstractmethod
from datetime import date

from domain.lecturas import LecturaTelemedida


class SuministroIngestionStrategy(ABC):
    @property
    @abstractmethod
    def nombre(self) -> str: ...

    @property
    @abstractmethod
    def soporta_perfiles(self) -> bool:
        """True si el tipo de medidor expone perfiles de 15 min (CLOU), False si solo
        admite granularidad diaria (NANSEN/CHUPETE). Ver ADR-003."""
        ...

    @abstractmethod
    async def leer_lecturas(
        self,
        medidor: str,
        srv_codigo: str,
        desde: date,
        hasta: date,
    ) -> list[LecturaTelemedida]: ...
