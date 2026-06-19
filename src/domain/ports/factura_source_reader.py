from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class FacturaResult:
    fecha_vencimiento: date | None


class FacturaSourceReader(ABC):
    @abstractmethod
    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        """Devuelve los datos de la factura vigente del suministro, o None si no hay."""
