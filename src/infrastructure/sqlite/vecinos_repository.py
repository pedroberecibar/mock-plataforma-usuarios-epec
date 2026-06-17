import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.vecinos_repository import VecinosRepository
from infrastructure.sqlite.models import Suministro


def _haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


class SQLiteVecinosRepository(VecinosRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_vecinos(self, suministro_id: str, radio_metros: float) -> list[str]:
        ref_result = await self._session.execute(
            select(Suministro.lat, Suministro.lon).where(Suministro.id == suministro_id)
        )
        ref_row = ref_result.one_or_none()
        if ref_row is None:
            return []

        lat_ref, lon_ref = ref_row.lat, ref_row.lon
        delta = radio_metros / 111_000.0

        candidates = await self._session.execute(
            select(Suministro.id, Suministro.lat, Suministro.lon)
            .where(Suministro.id != suministro_id)
            .where(Suministro.lat >= lat_ref - delta)
            .where(Suministro.lat <= lat_ref + delta)
            .where(Suministro.lon >= lon_ref - delta)
            .where(Suministro.lon <= lon_ref + delta)
        )

        return [
            row.id
            for row in candidates
            if _haversine_metros(lat_ref, lon_ref, row.lat, row.lon) <= radio_metros
        ]
