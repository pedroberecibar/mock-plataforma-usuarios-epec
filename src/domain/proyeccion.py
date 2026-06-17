from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ProyeccionMensual:
    suministro_id: str
    mes: date  # primer dia del mes
    metodo_aplicado: str  # "interanual" | "estacional" | "reciente" | "insuficiente"
    meses_usados_como_base: int
    dias_usados_como_base: int
    bandera_confianza: str  # "alta" | "media" | "baja" | "sin_datos"
    rango_inferior_kwh: float | None
    rango_superior_kwh: float | None
