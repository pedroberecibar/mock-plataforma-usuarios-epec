import calendar
from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.proyeccion import ProyeccionMensual


class CalcularProyeccionMensualUseCase:
    def __init__(
        self,
        consumo_repo: ConsumoDiarioRepository,
        proyeccion_repo: ProyeccionRepository,
    ) -> None:
        self._consumo_repo = consumo_repo
        self._proyeccion_repo = proyeccion_repo

    async def ejecutar(self, suministro_id: str, mes: date) -> ProyeccionMensual:
        mes_inicio = mes.replace(day=1)
        days_in_month = calendar.monthrange(mes.year, mes.month)[1]
        mes_fin = mes_inicio.replace(day=days_in_month)

        current_serie = await self._consumo_repo.get_serie(suministro_id, mes_inicio, mes_fin)
        dias_actuales = len(current_serie)

        proyeccion = await self._intentar_interanual(
            suministro_id, mes_inicio, current_serie, dias_actuales, days_in_month
        )
        if proyeccion is None:
            proyeccion = await self._intentar_estacional(
                suministro_id, mes_inicio, current_serie, dias_actuales
            )
        if proyeccion is None:
            proyeccion = self._calcular_reciente_o_insuficiente(
                suministro_id, mes_inicio, current_serie, dias_actuales, days_in_month
            )

        await self._proyeccion_repo.upsert_proyeccion(proyeccion)
        return proyeccion

    async def _intentar_interanual(
        self,
        suministro_id: str,
        mes_inicio: date,
        current_serie: list[tuple[date, float]],
        dias_actuales: int,
        days_in_month: int,
    ) -> ProyeccionMensual | None:
        if dias_actuales == 0:
            return None

        last_year_inicio = mes_inicio.replace(year=mes_inicio.year - 1)
        last_year_fin = last_year_inicio.replace(
            day=calendar.monthrange(last_year_inicio.year, last_year_inicio.month)[1]
        )
        last_year_serie = await self._consumo_repo.get_serie(
            suministro_id, last_year_inicio, last_year_fin
        )

        if len(last_year_serie) < 20:
            return None

        last_year_dict = {d.day: kwh for d, kwh in last_year_serie}
        current_days = sorted(d.day for d, _ in current_serie)

        total_current = sum(kwh for _, kwh in current_serie)
        total_same_period_last_year = sum(last_year_dict.get(dia, 0.0) for dia in current_days)
        total_last_year = sum(kwh for _, kwh in last_year_serie)

        if total_same_period_last_year > 0:
            ratio = total_current / total_same_period_last_year
            projected = ratio * total_last_year
        else:
            projected = total_last_year

        return ProyeccionMensual(
            suministro_id=suministro_id,
            mes=mes_inicio,
            metodo_aplicado="interanual",
            meses_usados_como_base=12,
            dias_usados_como_base=dias_actuales,
            bandera_confianza="alta",
            rango_inferior_kwh=round(projected * 0.9, 2),
            rango_superior_kwh=round(projected * 1.1, 2),
        )

    async def _intentar_estacional(
        self,
        suministro_id: str,
        mes_inicio: date,
        current_serie: list[tuple[date, float]],
        dias_actuales: int,
    ) -> ProyeccionMensual | None:
        if dias_actuales == 0:
            return None

        historical = await self._get_same_month_historical(
            suministro_id, mes_inicio.month, mes_inicio.year
        )
        if len(historical) < 2:
            return None

        avg_monthly = sum(total for _, total, _ in historical) / len(historical)

        return ProyeccionMensual(
            suministro_id=suministro_id,
            mes=mes_inicio,
            metodo_aplicado="estacional",
            meses_usados_como_base=len(historical),
            dias_usados_como_base=dias_actuales,
            bandera_confianza="media",
            rango_inferior_kwh=round(avg_monthly * 0.85, 2),
            rango_superior_kwh=round(avg_monthly * 1.15, 2),
        )

    async def _get_same_month_historical(
        self, suministro_id: str, month: int, current_year: int
    ) -> list[tuple[int, float, int]]:
        totals: list[tuple[int, float, int]] = []
        for years_back in range(1, 6):
            year = current_year - years_back
            days_in_hist = calendar.monthrange(year, month)[1]
            inicio = date(year, month, 1)
            fin = date(year, month, days_in_hist)
            serie = await self._consumo_repo.get_serie(suministro_id, inicio, fin)
            if len(serie) >= 20:
                totals.append((year, sum(kwh for _, kwh in serie), len(serie)))
        return totals

    def _calcular_reciente_o_insuficiente(
        self,
        suministro_id: str,
        mes_inicio: date,
        current_serie: list[tuple[date, float]],
        dias_actuales: int,
        days_in_month: int,
    ) -> ProyeccionMensual:
        if dias_actuales < 7:
            return ProyeccionMensual(
                suministro_id=suministro_id,
                mes=mes_inicio,
                metodo_aplicado="insuficiente",
                meses_usados_como_base=0,
                dias_usados_como_base=dias_actuales,
                bandera_confianza="sin_datos",
                rango_inferior_kwh=None,
                rango_superior_kwh=None,
            )

        last_7 = sorted(current_serie, key=lambda x: x[0])[-7:]
        avg_daily = sum(kwh for _, kwh in last_7) / 7
        projected = avg_daily * days_in_month

        return ProyeccionMensual(
            suministro_id=suministro_id,
            mes=mes_inicio,
            metodo_aplicado="reciente",
            meses_usados_como_base=0,
            dias_usados_como_base=dias_actuales,
            bandera_confianza="baja",
            rango_inferior_kwh=round(projected * 0.8, 2),
            rango_superior_kwh=round(projected * 1.2, 2),
        )
