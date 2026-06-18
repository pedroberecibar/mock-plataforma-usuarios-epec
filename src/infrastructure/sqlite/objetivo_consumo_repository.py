from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from infrastructure.sqlite.models import ObjetivoConsumo


class SQLiteObjetivoConsumoRepository(ObjetivoConsumoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_vigente(self, suministro_id: str) -> tuple[float, str, date] | None:
        result = await self._session.execute(
            select(ObjetivoConsumo)
            .where(ObjetivoConsumo.suministro_id == suministro_id)
            .order_by(ObjetivoConsumo.vigente_desde.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return (row.valor_kwh, row.origen, row.vigente_desde)

    async def upsert_objetivo(
        self, suministro_id: str, valor_kwh: float, origen: str, vigente_desde: date
    ) -> None:
        existing = await self._session.execute(
            select(ObjetivoConsumo)
            .where(ObjetivoConsumo.suministro_id == suministro_id)
            .where(ObjetivoConsumo.vigente_desde == vigente_desde)
        )
        row = existing.scalar_one_or_none()
        if row is not None:
            row.valor_kwh = valor_kwh
            row.origen = origen
        else:
            self._session.add(
                ObjetivoConsumo(
                    suministro_id=suministro_id,
                    valor_kwh=valor_kwh,
                    origen=origen,
                    vigente_desde=vigente_desde,
                )
            )
        await self._session.commit()
