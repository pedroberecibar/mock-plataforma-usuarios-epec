from datetime import date
from typing import TypedDict

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository


class ObjetivoResult(TypedDict):
    valor_kwh: float
    origen: str
    vigente_desde: date


class GetObjetivoConsumoUseCase:
    def __init__(self, repo: ObjetivoConsumoRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str) -> ObjetivoResult | None:
        resultado = await self._repo.get_vigente(suministro_id)
        if resultado is None:
            return None
        valor_kwh, origen, vigente_desde = resultado
        return ObjetivoResult(valor_kwh=valor_kwh, origen=origen, vigente_desde=vigente_desde)
