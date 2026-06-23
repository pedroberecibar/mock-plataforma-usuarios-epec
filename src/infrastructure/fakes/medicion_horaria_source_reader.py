import math
from datetime import date, timedelta

from domain.lecturas_horarias import LecturaHoraria
from domain.ports.medicion_horaria_source_reader import MedicionHorariaSourceReader

# ---------------------------------------------------------------------------
# Dataset semilla con granularidad horaria (lecturas acumulativas).
# Perfil sinusoidal: mayor consumo en horas 7-9 y 19-22.
# Incluye: gap de 2 horas (hora 3 y 4 del 2026-06-05), lectura con
# cdr_codigo='R' (debe filtrarse) y un duplicado intencional.
# ---------------------------------------------------------------------------

_EQUIPO = "91013496"
_SRV = "SRV-91013496"
_FECHA_INICIO = date(2026, 6, 1)
_DIAS = 30
_VALOR_INICIAL = 13_800.0


def _kwh_hora(hora: int) -> float:
    """Consumo incremental por hora según perfil sinusoidal (kWh)."""
    base = 0.3
    mañana = 0.6 * math.exp(-((hora - 8) ** 2) / 4.0)
    noche = 0.9 * math.exp(-((hora - 20) ** 2) / 6.0)
    return round(base + mañana + noche, 3)


def _generar_seed() -> list[LecturaHoraria]:
    lecturas: list[LecturaHoraria] = []
    acum = _VALOR_INICIAL
    fecha_gap = _FECHA_INICIO + timedelta(days=4)  # 2026-06-05

    for d in range(_DIAS):
        fecha = _FECHA_INICIO + timedelta(days=d)
        for h in range(24):
            # Gap intencional: omitir horas 3 y 4 del quinto día
            if fecha == fecha_gap and h in (3, 4):
                continue
            acum = round(acum + _kwh_hora(h), 3)
            lecturas.append(
                LecturaHoraria(
                    equipo=_EQUIPO,
                    srv_codigo=_SRV,
                    cdr_codigo="E",
                    fecha=fecha,
                    hora=h,
                    valor_kwh=acum,
                )
            )

    # Lectura con cdr_codigo != 'E' — debe filtrarse
    lecturas.append(LecturaHoraria(_EQUIPO, _SRV, "R", _FECHA_INICIO, 12, 999_999.0))
    # Duplicado intencional — mismo (equipo, fecha, hora, cdr='E')
    lecturas.append(LecturaHoraria(_EQUIPO, _SRV, "E", _FECHA_INICIO, 10, lecturas[10].valor_kwh))
    return lecturas


SEED_LECTURAS_HORARIAS: list[LecturaHoraria] = _generar_seed()


class FakeMedicionHorariaSourceReader(MedicionHorariaSourceReader):
    def __init__(self, lecturas: list[LecturaHoraria] | None = None) -> None:
        self._lecturas = lecturas if lecturas is not None else SEED_LECTURAS_HORARIAS

    async def leer_lecturas_horarias(
        self, desde: date, hasta: date, equipos: list[str] | None = None
    ) -> list[LecturaHoraria]:
        # Incluye un registro ancla anterior a `desde` por equipo para poder
        # calcular el consumo de la primera hora del rango.
        resultado: list[LecturaHoraria] = []
        for lectura in self._lecturas:
            if equipos is not None and lectura.equipo not in equipos:
                continue
            if desde <= lectura.fecha <= hasta:
                resultado.append(lectura)
            elif lectura.fecha < desde:
                # ancla: la más reciente antes del rango (se sobreescribe)
                existing = next(
                    (
                        i
                        for i, r in enumerate(resultado)
                        if r.equipo == lectura.equipo
                        and r.cdr_codigo == lectura.cdr_codigo
                        and r.fecha < desde
                    ),
                    None,
                )
                if existing is None:
                    resultado.append(lectura)
                elif resultado[existing].fecha < lectura.fecha or (
                    resultado[existing].fecha == lectura.fecha
                    and resultado[existing].hora < lectura.hora
                ):
                    resultado[existing] = lectura
        return resultado
