from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass
class FacturaResult:
    fecha_vencimiento: date | None
    importe: float | None = None
    periodo: str | None = None
    url_pdf: str | None = None
    pago_online: bool = False


@dataclass
class FacturaDocumento:
    """Un documento individual a pagar (un cliente puede tener varios)."""

    periodo: str | None
    importe: float | None
    fecha_vencimiento: date | None
    estado: str | None
    url_pdf: str | None


@dataclass
class FacturaCuenta:
    """Estado de deuda completo del suministro: todos los documentos + total."""

    documentos: list[FacturaDocumento] = field(default_factory=list)
    total_deuda: float = 0.0
    pago_online: bool = False


class FacturaSourceReader(ABC):
    @abstractmethod
    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        """Devuelve la factura vigente (vencimiento más próximo) del suministro, o None."""

    @abstractmethod
    async def get_cuenta_factura(self, suministro_id: str) -> FacturaCuenta | None:
        """Devuelve todos los documentos a pagar + deuda total, o None si no hay datos."""
