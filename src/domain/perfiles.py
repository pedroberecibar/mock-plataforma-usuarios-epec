"""Regla de dominio: qué tipos de medidor exponen perfiles de 15 min (ADR-003).

Única fuente de verdad de la capacidad "soporta perfiles", usada tanto por las
estrategias de ingesta como por la capa de presentación. Hoy solo CLOU; cuando EPEC
resuelva la infraestructura SCADA de NANSEN, se actualiza acá (y se implementa la
ingesta de sus perfiles en la estrategia correspondiente).
"""


def soporta_perfiles(telemedible: str | None) -> bool:
    """True si el tipo de medidor expone perfiles de 15 min (granularidad horaria)."""
    return (telemedible or "").upper() == "CLOU"
