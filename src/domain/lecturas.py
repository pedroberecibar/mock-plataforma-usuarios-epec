from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LecturaTelemedida:
    """Lectura cruda de un medidor EPEC, normalizada para consumo en el dominio."""

    equipo: str
    cdr_codigo: str
    fecha: date
    valor_kwh: float
