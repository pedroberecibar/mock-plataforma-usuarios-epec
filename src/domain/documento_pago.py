from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentoPago:
    periodo: str  # ej. "04/2026"
    nro_factura: str  # ej. "0001-00000123"
    importe: float  # importe en ARS
    fecha_vencimiento: str  # ej. "2026-05-15" (ISO) o formato EPEC
