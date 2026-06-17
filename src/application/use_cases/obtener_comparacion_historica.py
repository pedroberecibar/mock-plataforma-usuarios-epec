import calendar
from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


@dataclass(frozen=True)
class PeriodoConsumo:
    mes: date  # primer día del mes
    serie: list[tuple[date, float]]
    total_kwh: float | None  # None cuando serie está vacía


@dataclass(frozen=True)
class ComparacionHistorica:
    mes_actual: PeriodoConsumo
    mes_anterior: PeriodoConsumo
    mismo_mes_anio_anterior: PeriodoConsumo
    datos_hasta: date | None


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
    def __init__(self, repo: ConsumoDiarioRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str, mes: date) -> ComparacionHistorica:
        actual = _primer_dia(mes)
        anterior = _mes_anterior(actual)
        anio_anterior = actual.replace(year=actual.year - 1)

        mes_actual = await _get_periodo(self._repo, suministro_id, actual)
        mes_anterior = await _get_periodo(self._repo, suministro_id, anterior)
        mismo_mes_anio_anterior = await _get_periodo(self._repo, suministro_id, anio_anterior)
        datos_hasta = await self._repo.get_ultima_fecha(suministro_id)

        return ComparacionHistorica(
            mes_actual=mes_actual,
            mes_anterior=mes_anterior,
            mismo_mes_anio_anterior=mismo_mes_anio_anterior,
            datos_hasta=datos_hasta,
        )
