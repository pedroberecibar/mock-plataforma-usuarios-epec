from dataclasses import dataclass
from datetime import date, timedelta

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.vecinos_repository import VecinosRepository

_MIN_VECINOS = 5
_DIAS_SEMANA = 364  # 52 semanas exactas → mismo día-de-semana año anterior


@dataclass
class DetalleDiaResult:
    fecha: date
    kwh_dia: float | None
    kwh_mismo_dia_anio_ant: float | None
    kwh_promedio_zona: float | None
    n_vecinos: int


class GetDetalleDiaUseCase:
    def __init__(
        self,
        consumo_repo: ConsumoDiarioRepository,
        vecinos_repo: VecinosRepository,
    ) -> None:
        self._consumo_repo = consumo_repo
        self._vecinos_repo = vecinos_repo

    async def ejecutar(self, suministro_id: str, fecha: date) -> DetalleDiaResult:
        fecha_ant = fecha - timedelta(days=_DIAS_SEMANA)

        serie_dia = await self._consumo_repo.get_serie(suministro_id, fecha, fecha)
        kwh_dia = serie_dia[0][1] if serie_dia else None

        serie_ant = await self._consumo_repo.get_serie(suministro_id, fecha_ant, fecha_ant)
        kwh_mismo_dia_anio_ant = serie_ant[0][1] if serie_ant else None

        vecinos_ids = await self._vecinos_repo.get_vecinos(suministro_id, 150.0)
        totales_vecinos: list[float] = []
        for vid in vecinos_ids:
            serie_v = await self._consumo_repo.get_serie(vid, fecha_ant, fecha_ant)
            if serie_v:
                totales_vecinos.append(serie_v[0][1])

        n_vecinos = len(totales_vecinos)
        kwh_promedio_zona = sum(totales_vecinos) / n_vecinos if n_vecinos >= _MIN_VECINOS else None

        return DetalleDiaResult(
            fecha=fecha,
            kwh_dia=kwh_dia,
            kwh_mismo_dia_anio_ant=kwh_mismo_dia_anio_ant,
            kwh_promedio_zona=kwh_promedio_zona,
            n_vecinos=n_vecinos,
        )
