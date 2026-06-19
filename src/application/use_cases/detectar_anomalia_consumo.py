import math
from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository

_MIN_DIAS = 3
_DEFAULT_UMBRAL_Z = 2.0


@dataclass(frozen=True)
class AnomaliaResult:
    fecha: date
    kwh: float
    z_score: float
    desviacion_pct: float


class DetectarAnomaliaConsumoUseCase:
    def __init__(
        self,
        consumo_repo: ConsumoDiarioRepository,
        umbral_z: float = _DEFAULT_UMBRAL_Z,
    ) -> None:
        self._repo = consumo_repo
        self._umbral_z = umbral_z

    async def ejecutar(self, suministro_id: str, mes: date) -> AnomaliaResult | None:
        ultimo_dia = monthrange(mes.year, mes.month)[1]
        desde = date(mes.year, mes.month, 1)
        hasta = date(mes.year, mes.month, ultimo_dia)

        serie = await self._repo.get_serie(suministro_id, desde, hasta)
        if len(serie) < _MIN_DIAS:
            return None

        valores = [kwh for _, kwh in serie]
        n = len(valores)
        media = sum(valores) / n
        varianza = sum((v - media) ** 2 for v in valores) / n
        std = math.sqrt(varianza)

        if std == 0:
            return None

        ultima_fecha, ultimo_kwh = serie[-1]
        z = (ultimo_kwh - media) / std

        if z <= self._umbral_z:
            return None

        desviacion_pct = ((ultimo_kwh - media) / media) * 100 if media != 0 else 0.0
        return AnomaliaResult(
            fecha=ultima_fecha,
            kwh=ultimo_kwh,
            z_score=z,
            desviacion_pct=desviacion_pct,
        )
