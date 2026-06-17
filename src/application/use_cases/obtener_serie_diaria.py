from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


@dataclass(frozen=True)
class SerieDiaria:
    serie: list[tuple[date, float]]
    datos_hasta: date | None


class ObtenerSerieDiariaUseCase:
    def __init__(self, repo: ConsumoDiarioRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str, desde: date, hasta: date) -> SerieDiaria:
        serie = await self._repo.get_serie(suministro_id, desde, hasta)
        datos_hasta = await self._repo.get_ultima_fecha(suministro_id)
        return SerieDiaria(serie=serie, datos_hasta=datos_hasta)
