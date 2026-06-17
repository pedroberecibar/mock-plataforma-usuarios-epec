from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LecturaTelemedida:
    """Lectura cruda de un medidor EPEC, normalizada para consumo en el dominio."""

    equipo: str  # STE_NUMERO / med_numero_equipo — identifica el dispositivo físico
    srv_codigo: str  # SRV_CODIGO de Oracle — suministro (punto de medición) al que pertenece
    cdr_codigo: str
    fecha: date
    valor_kwh: float
