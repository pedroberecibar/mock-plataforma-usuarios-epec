from datetime import date
from typing import Any

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository


class SQLiteObjetivoConsumoRepository(ObjetivoConsumoRepository):
    """Adapter SQLite — implementación pendiente (ver Sprint 4)."""

    def __init__(self, session: Any) -> None:
        self._session = session

    async def get_vigente(self, suministro_id: str) -> tuple[float, str, date] | None:
        raise NotImplementedError

    async def upsert_objetivo(
        self, suministro_id: str, valor_kwh: float, origen: str, vigente_desde: date
    ) -> None:
        raise NotImplementedError
