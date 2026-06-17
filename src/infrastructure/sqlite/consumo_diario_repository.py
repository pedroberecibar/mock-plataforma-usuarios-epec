from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from infrastructure.sqlite.models import ConsumoDiario


class SQLiteConsumoDiarioRepository(ConsumoDiarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_serie(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, float]]:
        result = await self._session.execute(
            select(ConsumoDiario.fecha, ConsumoDiario.kwh)
            .where(ConsumoDiario.suministro_id == suministro_id)
            .where(ConsumoDiario.fecha >= desde)
            .where(ConsumoDiario.fecha <= hasta)
            .order_by(ConsumoDiario.fecha)
        )
        return [(row.fecha, row.kwh) for row in result]

    async def upsert_consumo(self, suministro_id: str, fecha: date, kwh: float) -> None:
        stmt = (
            insert(ConsumoDiario)
            .values(suministro_id=suministro_id, fecha=fecha, kwh=kwh)
            .on_conflict_do_update(
                index_elements=["suministro_id", "fecha"],
                set_={"kwh": kwh},
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_ultima_fecha(self, suministro_id: str) -> date | None:
        result = await self._session.execute(
            select(func.max(ConsumoDiario.fecha)).where(
                ConsumoDiario.suministro_id == suministro_id
            )
        )
        return result.scalar_one_or_none()
