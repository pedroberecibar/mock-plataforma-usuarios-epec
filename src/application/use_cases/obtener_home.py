import calendar
from dataclasses import dataclass
from datetime import UTC, date, datetime

from application.use_cases.calcular_proyeccion_mensual import CalcularProyeccionMensualUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.ports.vecinos_repository import VecinosRepository
from domain.proyeccion import ProyeccionMensual

_MIN_VECINOS = 5


@dataclass(frozen=True)
class ConsumoMes:
    total_kwh: float | None
    vs_mes_anterior_pct: float | None
    vs_anio_anterior_pct: float | None


@dataclass(frozen=True)
class ComparacionZona:
    promedio_vecinos_kwh: float | None
    n_vecinos: int
    diferencia_pct: float | None


@dataclass(frozen=True)
class HomeData:
    consumo_mes: ConsumoMes
    comparacion_zona: ComparacionZona
    proyeccion: ProyeccionMensual
    datos_hasta: date | None
    timestamp: datetime


class ObtenerHomeUseCase:
    def __init__(
        self,
        consumo_repo: ConsumoDiarioRepository,
        vecinos_repo: VecinosRepository,
        proyeccion_repo: ProyeccionRepository,
        calcular_proyeccion_uc: CalcularProyeccionMensualUseCase,
    ) -> None:
        self._consumo_repo = consumo_repo
        self._vecinos_repo = vecinos_repo
        self._proyeccion_repo = proyeccion_repo
        self._calcular_proyeccion_uc = calcular_proyeccion_uc

    async def ejecutar(self, suministro_id: str, mes: date) -> HomeData:
        mes_inicio = mes.replace(day=1)
        days_in_month = calendar.monthrange(mes.year, mes.month)[1]
        mes_fin = mes_inicio.replace(day=days_in_month)

        current_serie = await self._consumo_repo.get_serie(suministro_id, mes_inicio, mes_fin)
        total_kwh: float | None = sum(kwh for _, kwh in current_serie) if current_serie else None
        dias_transcurridos = len(current_serie)

        vs_mes_anterior_pct = await self._calcular_vs_mes_anterior(
            suministro_id, mes_inicio, current_serie, total_kwh, dias_transcurridos
        )
        vs_anio_anterior_pct = await self._calcular_vs_anio_anterior(
            suministro_id, mes_inicio, current_serie, total_kwh, dias_transcurridos
        )

        consumo_mes = ConsumoMes(
            total_kwh=total_kwh,
            vs_mes_anterior_pct=vs_mes_anterior_pct,
            vs_anio_anterior_pct=vs_anio_anterior_pct,
        )

        comparacion_zona = await self._calcular_zona(
            suministro_id, mes_inicio, mes_fin, total_kwh, dias_transcurridos
        )

        proyeccion = await self._proyeccion_repo.get_proyeccion(suministro_id, mes_inicio)
        if proyeccion is None:
            proyeccion = await self._calcular_proyeccion_uc.ejecutar(suministro_id, mes_inicio)

        datos_hasta = await self._consumo_repo.get_ultima_fecha(suministro_id)

        return HomeData(
            consumo_mes=consumo_mes,
            comparacion_zona=comparacion_zona,
            proyeccion=proyeccion,
            datos_hasta=datos_hasta,
            timestamp=datetime.now(UTC),
        )

    async def _calcular_vs_mes_anterior(
        self,
        suministro_id: str,
        mes_inicio: date,
        current_serie: list[tuple[date, float]],
        total_kwh: float | None,
        dias_transcurridos: int,
    ) -> float | None:
        if total_kwh is None or dias_transcurridos == 0:
            return None

        if mes_inicio.month == 1:
            prev_inicio = date(mes_inicio.year - 1, 12, 1)
        else:
            prev_inicio = date(mes_inicio.year, mes_inicio.month - 1, 1)

        days_in_prev = calendar.monthrange(prev_inicio.year, prev_inicio.month)[1]
        prev_fin = prev_inicio.replace(day=min(dias_transcurridos, days_in_prev))

        prev_serie = await self._consumo_repo.get_serie(suministro_id, prev_inicio, prev_fin)
        prev_total = sum(kwh for _, kwh in prev_serie) if prev_serie else 0.0
        if prev_total <= 0:
            return None

        return round((total_kwh - prev_total) / prev_total * 100, 2)

    async def _calcular_vs_anio_anterior(
        self,
        suministro_id: str,
        mes_inicio: date,
        current_serie: list[tuple[date, float]],
        total_kwh: float | None,
        dias_transcurridos: int,
    ) -> float | None:
        if total_kwh is None or dias_transcurridos == 0:
            return None

        last_year_inicio = mes_inicio.replace(year=mes_inicio.year - 1)
        days_in_last_year_month = calendar.monthrange(
            last_year_inicio.year, last_year_inicio.month
        )[1]
        last_year_fin = last_year_inicio.replace(
            day=min(dias_transcurridos, days_in_last_year_month)
        )

        last_year_serie = await self._consumo_repo.get_serie(
            suministro_id, last_year_inicio, last_year_fin
        )
        last_year_total = sum(kwh for _, kwh in last_year_serie) if last_year_serie else 0.0
        if last_year_total <= 0:
            return None

        return round((total_kwh - last_year_total) / last_year_total * 100, 2)

    async def _calcular_zona(
        self,
        suministro_id: str,
        mes_inicio: date,
        mes_fin: date,
        total_kwh: float | None,
        dias_transcurridos: int,
    ) -> ComparacionZona:
        vecinos = await self._vecinos_repo.get_vecinos(suministro_id, 150.0)
        n_vecinos = len(vecinos)

        if n_vecinos < _MIN_VECINOS or dias_transcurridos == 0:
            return ComparacionZona(
                promedio_vecinos_kwh=None, n_vecinos=n_vecinos, diferencia_pct=None
            )

        vecino_totals: list[float] = []
        for vecino_id in vecinos:
            serie = await self._consumo_repo.get_serie(vecino_id, mes_inicio, mes_fin)
            if serie:
                vecino_totals.append(sum(kwh for _, kwh in serie))

        if not vecino_totals:
            return ComparacionZona(
                promedio_vecinos_kwh=None, n_vecinos=n_vecinos, diferencia_pct=None
            )

        promedio = sum(vecino_totals) / len(vecino_totals)
        diferencia_pct: float | None = None
        if promedio > 0 and total_kwh is not None:
            diferencia_pct = round((total_kwh - promedio) / promedio * 100, 2)

        return ComparacionZona(
            promedio_vecinos_kwh=round(promedio, 2),
            n_vecinos=n_vecinos,
            diferencia_pct=diferencia_pct,
        )
