"""Dominio de la sección "Mi cuenta".

`CuentaSuministroRaw` es la representación cruda de los datos del suministro tal
como vienen de la fuente externa (Oracle). Incluye PII en claro (nro_documento,
cuit) que vive solo en memoria — nunca se loguea ni se persiste sin cifrar.

Las funciones puras de este módulo normalizan/derivan campos para la respuesta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CuentaSuministroRaw:
    razon_social: str | None
    tipo_documento: str | None
    nro_documento: str | None
    cuit: str | None
    calle: str | None
    altura: str | None
    piso: str | None
    depto: str | None
    torre: str | None
    barrio: str | None
    localidad: str | None
    cp: str | None
    datos_adicionales: str | None
    estado_servicio: str | None
    telemedible: str | None  # marca del medidor (CLOU/NANSEN/CHUPETE/GC)
    medidor: str | None
    telemedible_desde: date | None
    codigo_tarifa: str | None
    tarifa: str | None  # descriptor legible, ej. "1.a/f RESIDENCIAL"
    grupo_tarifario: str | None
    clase: str | None
    clase_descripcion: str | None
    tension: str | None
    medidor_fases: str | None  # crudo: MON/TRI/TRIF/0/None


def normalizar_fase(raw: str | None) -> str:
    """MON→Monofásico, TRI/TRIF→Trifásico, resto/None→Desconocido."""
    if raw is None:
        return "Desconocido"
    valor = raw.strip().upper()
    if valor.startswith("MON"):
        return "Monofásico"
    if valor.startswith("TRI"):
        return "Trifásico"
    return "Desconocido"


def componer_direccion(raw: CuentaSuministroRaw) -> str | None:
    """Arma una dirección legible saltando los componentes faltantes."""
    if not raw.calle:
        return None
    partes = [raw.calle.strip()]
    if raw.altura:
        partes.append(str(raw.altura).strip())
    direccion = " ".join(partes)

    extras = []
    if raw.piso:
        extras.append(f"Piso {raw.piso.strip()}")
    if raw.depto:
        extras.append(f"Depto {raw.depto.strip()}")
    if raw.torre:
        extras.append(f"Torre {raw.torre.strip()}")
    if extras:
        direccion = f"{direccion} {' '.join(extras)}"

    if raw.datos_adicionales:
        direccion = f"{direccion} ({raw.datos_adicionales.strip()})"
    return direccion


def enmascarar(valor: str | None, visibles: int = 4) -> str | None:
    """Devuelve el valor con todos los caracteres ocultos salvo los últimos `visibles`."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    if len(texto) <= visibles:
        return "*" * len(texto)
    return "*" * (len(texto) - visibles) + texto[-visibles:]
