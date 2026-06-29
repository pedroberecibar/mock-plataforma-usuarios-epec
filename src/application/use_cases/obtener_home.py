import asyncio
import calendar
from dataclasses import dataclass
from datetime import UTC, date, datetime

from application.use_cases.calcular_proyeccion_mensual import CalcularProyeccionMensualUseCase
from domain.comparacion_periodo import dias_con_dato, total_en_dias, variacion_pct
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
    n_vecinos_con_datos: int
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

        # Kick off vecinos early: while SQLite queries run, Oracle (or cache) starts in background
        vecinos_task: asyncio.Task[list[str]] = asyncio.ensure_future(
            self._vecinos_repo.get_vecinos(suministro_id)
        )

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

        # Collect vecinos result (likely already done if cache hit, otherwise wait up to 3s)
        vecinos = await vecinos_task
        ultimo_dia_usuario = current_serie[-1][0] if current_serie else None
        comparacion_zona = await self._calcular_zona(
            suministro_id,
            mes_inicio,
            mes_fin,
            total_kwh,
            dias_transcurridos,
            vecinos,
            ultimo_dia_usuario,
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

        base = await self._total_mismo_periodo(suministro_id, prev_inicio, current_serie)
        return variacion_pct(total_kwh, base)

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
        base = await self._total_mismo_periodo(suministro_id, last_year_inicio, current_serie)
        return variacion_pct(total_kwh, base)

    async def _total_mismo_periodo(
        self,
        suministro_id: str,
        mes_inicio_comparacion: date,
        current_serie: list[tuple[date, float]],
    ) -> float:
        """Total del mes de comparación restringido a los mismos días calendario
        que tienen dato en el mes en curso (comparación a igual período)."""
        days = calendar.monthrange(mes_inicio_comparacion.year, mes_inicio_comparacion.month)[1]
        fin = mes_inicio_comparacion.replace(day=days)
        serie = await self._consumo_repo.get_serie(suministro_id, mes_inicio_comparacion, fin)
        return total_en_dias(serie, dias_con_dato(current_serie))

    async def _calcular_zona(
        self,
        suministro_id: str,
        mes_inicio: date,
        mes_fin: date,
        total_kwh: float | None,
        dias_transcurridos: int,
        vecinos: list[str],
        ultimo_dia_usuario: date | None,
    ) -> ComparacionZona:
        n_vecinos = len(vecinos)

        _sin_datos = ComparacionZona(
            promedio_vecinos_kwh=None,
            n_vecinos=n_vecinos,
            n_vecinos_con_datos=0,
            diferencia_pct=None,
        )

        if n_vecinos < _MIN_VECINOS or dias_transcurridos == 0 or total_kwh is None:
            return _sin_datos

        # Limitar el período de vecinos al último día con dato del usuario para comparación justa
        hasta_efectivo = min(mes_fin, ultimo_dia_usuario) if ultimo_dia_usuario else mes_fin

        totales = await self._consumo_repo.get_totales_por_suministro(
            vecinos, mes_inicio, hasta_efectivo
        )

        if len(totales) < _MIN_VECINOS:
            return _sin_datos

        promedio = sum(kwh for _, kwh in totales) / len(totales)
        diferencia_pct: float | None = None
        if promedio > 0:
            diferencia_pct = round((total_kwh - promedio) / promedio * 100, 2)

        return ComparacionZona(
            promedio_vecinos_kwh=round(promedio, 2),
            n_vecinos=n_vecinos,
            n_vecinos_con_datos=len(totales),
            diferencia_pct=diferencia_pct,
        )
