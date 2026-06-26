from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class FacturaResult:
    fecha_vencimiento: date | None
    importe: float | None = None
    periodo: str | None = None
    url_pdf: str | None = None
    pago_online: bool = False


class FacturaSourceReader(ABC):
    @abstractmethod
    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        """Devuelve los datos de la factura vigente del suministro, o None si no hay."""
