from datetime import date

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository


class FakeObjetivoConsumoRepository(ObjetivoConsumoRepository):
    def __init__(self) -> None:
        self._objetivos: dict[str, list[tuple[float, str, date]]] = {}

    async def get_vigente(self, suministro_id: str) -> tuple[float, str, date] | None:
        objetivos = self._objetivos.get(suministro_id)
        if not objetivos:
            return None
        return max(objetivos, key=lambda objetivo: objetivo[2])

    async def upsert_objetivo(
        self, suministro_id: str, valor_kwh: float, origen: str, vigente_desde: date
    ) -> None:
        self._objetivos.setdefault(suministro_id, []).append((valor_kwh, origen, vigente_desde))
