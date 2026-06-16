from typing import Any

from domain.ports.vecinos_repository import VecinosRepository


class SQLiteVecinosRepository(VecinosRepository):
    """Adapter SQLite (bounding box + Haversine) — implementación pendiente (ver Sprint 3)."""

    def __init__(self, session: Any) -> None:
        self._session = session

    async def get_vecinos(self, suministro_id: str, radio_metros: float) -> list[str]:
        raise NotImplementedError
