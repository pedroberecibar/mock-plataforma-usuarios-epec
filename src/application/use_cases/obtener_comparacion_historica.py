import calendar
from dataclasses import dataclass
from datetime import date

from domain.comparacion_periodo import dias_con_dato, total_en_dias, variacion_pct
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.vecinos_repository import VecinosRepository

_MIN_VECINOS = 5


@dataclass(frozen=True)
class PeriodoConsumo:
    mes: date  # primer día del mes
    serie: list[tuple[date, float]]
    total_kwh: float | None  # None cuando serie está vacía


@dataclass(frozen=True)
class ZonaResumen:
    promedio_vecinos_kwh: float | None
    n_vecinos: int
    diferencia_pct: float | None
    serie: list[tuple[date, float]]


@dataclass(frozen=True)
class ComparacionHistorica:
    mes_actual: PeriodoConsumo
    mes_anterior: PeriodoConsumo
    mismo_mes_anio_anterior: PeriodoConsumo
    zona_mes_actual: ZonaResumen
    datos_hasta: date | None
    # Variación a igual período (mismos días calendario que el mes en curso).
    vs_mes_anterior_pct: float | None
    vs_anio_anterior_pct: float | None


def _primer_dia(mes: date) -> date:
    return mes.replace(day=1)


def _ultimo_dia(primer_dia: date) -> date:
    _, ultimo = calendar.monthrange(primer_dia.year, primer_dia.month)
    return primer_dia.replace(day=ultimo)


def _mes_anterior(primer_dia: date) -> date:
    if primer_dia.month == 1:
        return primer_dia.replace(year=primer_dia.year - 1, month=12)
    return primer_dia.replace(month=primer_dia.month - 1)


async def _get_periodo(
    repo: ConsumoDiarioRepository, suministro_id: str, primer: date
) -> PeriodoConsumo:
    serie = await repo.get_serie(suministro_id, primer, _ultimo_dia(primer))
    total = round(sum(kwh for _, kwh in serie), 2) if serie else None
    return PeriodoConsumo(mes=primer, serie=serie, total_kwh=total)


class ObtenerComparacionHistoricaUseCase:
    def __init__(
        self,
        repo: ConsumoDiarioRepository,
        vecinos_repo: VecinosRepository | None = None,
    ) -> None:
        self._repo = repo
        self._vecinos_repo = vecinos_repo

    async def ejecutar(self, suministro_id: str, mes: date) -> ComparacionHistorica:
        actual = _primer_dia(mes)
        anterior = _mes_anterior(actual)
        anio_anterior = actual.replace(year=actual.year - 1)

        mes_actual = await _get_periodo(self._repo, suministro_id, actual)
        mes_anterior = await _get_periodo(self._repo, suministro_id, anterior)
        mismo_mes_anio_anterior = await _get_periodo(self._repo, suministro_id, anio_anterior)
        datos_hasta = await self._repo.get_ultima_fecha(suministro_id)
        zona_mes_actual = await self._calcular_zona(
            suministro_id, actual, mes_actual.total_kwh, len(mes_actual.serie)
        )

        # Variación a igual período: comparar el mes en curso contra los mismos
        # días calendario del mes anterior / año anterior (no el mes completo).
        dias_actuales = dias_con_dato(mes_actual.serie)
        vs_mes_anterior_pct = variacion_pct(
            mes_actual.total_kwh, total_en_dias(mes_anterior.serie, dias_actuales)
        )
        vs_anio_anterior_pct = variacion_pct(
            mes_actual.total_kwh, total_en_dias(mismo_mes_anio_anterior.serie, dias_actuales)
        )

        return ComparacionHistorica(
            mes_actual=mes_actual,
            mes_anterior=mes_anterior,
            mismo_mes_anio_anterior=mismo_mes_anio_anterior,
            zona_mes_actual=zona_mes_actual,
            datos_hasta=datos_hasta,
            vs_mes_anterior_pct=vs_mes_anterior_pct,
            vs_anio_anterior_pct=vs_anio_anterior_pct,
        )

    async def _calcular_zona(
        self,
        suministro_id: str,
        mes_inicio: date,
        total_kwh: float | None,
        dias_transcurridos: int,
    ) -> ZonaResumen:
        _empty = ZonaResumen(promedio_vecinos_kwh=None, n_vecinos=0, diferencia_pct=None, serie=[])
        if self._vecinos_repo is None:
            return _empty

        vecinos = await self._vecinos_repo.get_vecinos(suministro_id)
        n_vecinos = len(vecinos)
        if n_vecinos < _MIN_VECINOS or dias_transcurridos == 0 or total_kwh is None:
            return ZonaResumen(
                promedio_vecinos_kwh=None, n_vecinos=n_vecinos, diferencia_pct=None, serie=[]
            )

        mes_fin = _ultimo_dia(mes_inicio)

        # Validar umbral de privacidad con totales individuales
        vecino_totals: list[float] = []
        for vecino_id in vecinos:
            serie_v = await self._repo.get_serie(vecino_id, mes_inicio, mes_fin)
            if serie_v:
                vecino_totals.append(sum(kwh for _, kwh in serie_v))

        if len(vecino_totals) < _MIN_VECINOS:
            return ZonaResumen(
                promedio_vecinos_kwh=None, n_vecinos=n_vecinos, diferencia_pct=None, serie=[]
            )

        promedio = sum(vecino_totals) / len(vecino_totals)
        diferencia_pct: float | None = None
        if promedio > 0:
            diferencia_pct = round((total_kwh - promedio) / promedio * 100, 2)

        # Serie diaria de promedio de vecinos para el gráfico
        serie_zona = await self._repo.get_serie_promedio_zona(vecinos, mes_inicio, mes_fin)

        return ZonaResumen(
            promedio_vecinos_kwh=round(promedio, 2),
            n_vecinos=n_vecinos,
            diferencia_pct=diferencia_pct,
            serie=serie_zona,
        )
