from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.suministro_repository import SuministroRepository
from infrastructure.sqlite.models import Suministro


class SQLiteSuministroRepository(SuministroRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def existe(self, suministro_id: str) -> bool:
        result = await self._session.execute(
            select(Suministro.id).where(Suministro.id == suministro_id)
        )
        return result.scalar_one_or_none() is not None

    async def crear_placeholder(self, suministro_id: str) -> None:
        stmt = (
            insert(Suministro)
            .values(id=suministro_id, lat=0.0, lon=0.0, suministro_referencia=suministro_id)
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await self._session.execute(stmt)

    async def upsert_coordenadas(self, suministro_id: str, lat: float, lon: float) -> None:
        stmt = (
            insert(Suministro)
            .values(id=suministro_id, lat=lat, lon=lon, suministro_referencia=suministro_id)
            .on_conflict_do_update(
                index_elements=["id"],
                set_={"lat": lat, "lon": lon},
            )
        )
        await self._session.execute(stmt)
