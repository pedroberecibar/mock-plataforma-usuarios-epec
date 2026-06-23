from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.consumo_horario_repository import ConsumoHorarioRepository
from infrastructure.sqlite.models import ConsumoHorario


class SQLiteConsumoHorarioRepository(ConsumoHorarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_serie_horaria(self, suministro_id: str, fecha: date) -> list[tuple[int, float]]:
        result = await self._session.execute(
            select(ConsumoHorario.hora, ConsumoHorario.kwh)
            .where(ConsumoHorario.suministro_id == suministro_id)
            .where(ConsumoHorario.fecha == fecha)
            .order_by(ConsumoHorario.hora)
        )
        return [(row.hora, row.kwh) for row in result]

    async def upsert_consumo_horario(
        self, suministro_id: str, fecha: date, hora: int, kwh: float
    ) -> None:
        stmt = (
            insert(ConsumoHorario)
            .values(suministro_id=suministro_id, fecha=fecha, hora=hora, kwh=kwh)
            .on_conflict_do_update(
                index_elements=["suministro_id", "fecha", "hora"],
                set_={"kwh": kwh},
            )
        )
        await self._session.execute(stmt)

    async def get_ultima_fecha_horaria(self, suministro_id: str) -> date | None:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.max(ConsumoHorario.fecha)).where(
                ConsumoHorario.suministro_id == suministro_id
            )
        )
        return result.scalar_one_or_none()

    async def get_serie_horaria_rango(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, int, float]]:
        result = await self._session.execute(
            select(ConsumoHorario.fecha, ConsumoHorario.hora, ConsumoHorario.kwh)
            .where(ConsumoHorario.suministro_id == suministro_id)
            .where(ConsumoHorario.fecha >= desde)
            .where(ConsumoHorario.fecha <= hasta)
            .order_by(ConsumoHorario.fecha, ConsumoHorario.hora)
        )
        return [(row.fecha, row.hora, row.kwh) for row in result]
