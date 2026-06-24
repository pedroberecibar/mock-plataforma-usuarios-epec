import calendar
from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.vecinos_repository import VecinosRepository

_MIN_VECINOS = 5


@dataclass
class ObjetivoSugeridoResult:
    valor_kwh: float | None
    n_vecinos: int
    sin_datos: bool


class CalcularObjetivoSugeridoUseCase:
    def __init__(
        self,
        vecinos_repo: VecinosRepository,
        consumo_repo: ConsumoDiarioRepository,
    ) -> None:
        self._vecinos_repo = vecinos_repo
        self._consumo_repo = consumo_repo

    async def ejecutar(self, suministro_id: str, mes: date) -> ObjetivoSugeridoResult:
        """Calcula el promedio de consumo mensual de vecinos en 150 m para el mismo
        mes del año anterior. Devuelve sin_datos=True si hay menos de 5 vecinos con datos
        (privacidad — Ley 25.326)."""
        mes_ref = date(mes.year - 1, mes.month, 1)
        last_day = calendar.monthrange(mes_ref.year, mes_ref.month)[1]
        desde = mes_ref
        hasta = date(mes_ref.year, mes_ref.month, last_day)

        vecinos_ids = await self._vecinos_repo.get_vecinos(suministro_id)

        totales: list[float] = []
        for vid in vecinos_ids:
            serie = await self._consumo_repo.get_serie(vid, desde, hasta)
            if serie:
                totales.append(sum(kwh for _, kwh in serie))

        n_con_datos = len(totales)
        if n_con_datos < _MIN_VECINOS:
            return ObjetivoSugeridoResult(
                valor_kwh=None,
                n_vecinos=n_con_datos,
                sin_datos=True,
            )

        return ObjetivoSugeridoResult(
            valor_kwh=sum(totales) / n_con_datos,
            n_vecinos=n_con_datos,
            sin_datos=False,
        )
