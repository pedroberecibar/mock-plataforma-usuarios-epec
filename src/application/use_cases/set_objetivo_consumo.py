from datetime import date

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository


class SetObjetivoConsumoUseCase:
    def __init__(self, repo: ObjetivoConsumoRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str, valor_kwh: float) -> None:
        if valor_kwh <= 0:
            raise ValueError("El objetivo debe ser un valor positivo en kWh")
        await self._repo.upsert_objetivo(suministro_id, valor_kwh, "manual", date.today())
