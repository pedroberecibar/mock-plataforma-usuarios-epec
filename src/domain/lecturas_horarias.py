from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LecturaHoraria:
    """Lectura cruda de un medidor EPEC con granularidad horaria."""

    equipo: str
    srv_codigo: str
    cdr_codigo: str
    fecha: date
    hora: int  # 0-23
    valor_kwh: float  # lectura acumulada del contador en ese instante
