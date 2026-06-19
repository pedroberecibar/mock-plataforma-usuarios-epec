import calendar
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

from application.use_cases.calcular_objetivo_sugerido import CalcularObjetivoSugeridoUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from domain.ports.vecinos_repository import VecinosRepository

TextoDinamico = Literal["bajo_ritmo", "en_ritmo", "sobre_ritmo", "agotado", "sin_objetivo"]

_MARGEN = 0.05


@dataclass
class EstadoObjetivoResult:
    # Indicador 1
    objetivo_kwh: float | None
    promedio_vecinos_kwh: float | None
    n_vecinos: int
    diferencia_pct: float | None

    # Indicador 2
    dias_transcurridos: int
    dias_objetivo_consumidos: float | None
    texto_dinamico: TextoDinamico
    excedente_kwh: float | None

    # Indicador 3
    consumo_diario_real_kwh: float | None
    consumo_diario_objetivo_kwh: float | None


class CalcularEstadoObjetivoUseCase:
    def __init__(
        self,
        objetivo_repo: ObjetivoConsumoRepository,
        consumo_repo: ConsumoDiarioRepository,
        vecinos_repo: VecinosRepository,
    ) -> None:
        self._objetivo_repo = objetivo_repo
        self._consumo_repo = consumo_repo
        self._vecinos_repo = vecinos_repo

    async def ejecutar(
        self,
        suministro_id: str,
        mes: date,
        hoy: date | None = None,
    ) -> EstadoObjetivoResult:
        hoy_real = hoy or datetime.now(UTC).date()
        dias_del_mes = calendar.monthrange(mes.year, mes.month)[1]
        dias_transcurridos = (
            min(hoy_real.day, dias_del_mes)
            if (hoy_real.year == mes.year and hoy_real.month == mes.month)
            else dias_del_mes
        )

        objetivo = await self._objetivo_repo.get_vigente(suministro_id)
        if objetivo is None:
            return EstadoObjetivoResult(
                objetivo_kwh=None,
                promedio_vecinos_kwh=None,
                n_vecinos=0,
                diferencia_pct=None,
                dias_transcurridos=dias_transcurridos,
                dias_objetivo_consumidos=None,
                texto_dinamico="sin_objetivo",
                excedente_kwh=None,
                consumo_diario_real_kwh=None,
                consumo_diario_objetivo_kwh=None,
            )

        objetivo_kwh, _, _ = objetivo

        # --- Serie de consumo del mes ---
        desde = mes.replace(day=1)
        hasta = min(hoy_real, date(mes.year, mes.month, dias_del_mes))
        serie = await self._consumo_repo.get_serie(suministro_id, desde, hasta)
        consumo_acumulado = sum(kwh for _, kwh in serie)

        # --- Indicador 1: vs zona ---
        sugerido_uc = CalcularObjetivoSugeridoUseCase(self._vecinos_repo, self._consumo_repo)
        sugerido = await sugerido_uc.ejecutar(suministro_id, mes)
        promedio_vecinos = sugerido.valor_kwh if not sugerido.sin_datos else None
        n_vecinos = sugerido.n_vecinos
        diferencia_pct: float | None = None
        if promedio_vecinos is not None and promedio_vecinos > 0:
            diferencia_pct = (objetivo_kwh - promedio_vecinos) / promedio_vecinos * 100.0

        # --- Indicador 2: días objetivo consumidos ---
        ritmo_diario = objetivo_kwh / dias_del_mes
        consumo_diario_objetivo = ritmo_diario

        texto_dinamico: TextoDinamico
        excedente_kwh: float | None = None
        dias_objetivo_consumidos: float | None = None

        if consumo_acumulado >= objetivo_kwh:
            texto_dinamico = "agotado"
            excedente_kwh = consumo_acumulado - objetivo_kwh
            dias_objetivo_consumidos = dias_del_mes  # satura en días del mes
        else:
            dias_objetivo_consumidos = consumo_acumulado / ritmo_diario
            margen_inf = dias_transcurridos * (1 - _MARGEN)
            margen_sup = dias_transcurridos * (1 + _MARGEN)
            if dias_objetivo_consumidos < margen_inf:
                texto_dinamico = "bajo_ritmo"
            elif dias_objetivo_consumidos > margen_sup:
                texto_dinamico = "sobre_ritmo"
            else:
                texto_dinamico = "en_ritmo"

        # --- Indicador 3: consumo diario real ---
        consumo_diario_real: float | None = None
        if serie:
            consumo_diario_real = serie[-1][1]  # último día con dato

        return EstadoObjetivoResult(
            objetivo_kwh=objetivo_kwh,
            promedio_vecinos_kwh=promedio_vecinos,
            n_vecinos=n_vecinos,
            diferencia_pct=diferencia_pct,
            dias_transcurridos=dias_transcurridos,
            dias_objetivo_consumidos=dias_objetivo_consumidos,
            texto_dinamico=texto_dinamico,
            excedente_kwh=excedente_kwh,
            consumo_diario_real_kwh=consumo_diario_real,
            consumo_diario_objetivo_kwh=consumo_diario_objetivo,
        )
