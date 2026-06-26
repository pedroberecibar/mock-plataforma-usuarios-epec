from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.cuenta_sensible_repository import CuentaSensibleRepository
from infrastructure.sqlite.models import CuentaDatosSensibles


class SQLiteCuentaSensibleRepository(CuentaSensibleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(
        self, suministro_id: str, nro_documento_enc: str | None, cuit_enc: str | None
    ) -> None:
        stmt = (
            insert(CuentaDatosSensibles)
            .values(
                suministro_id=suministro_id,
                nro_documento_enc=nro_documento_enc,
                cuit_enc=cuit_enc,
                actualizado_en=datetime.now(UTC),
            )
            .on_conflict_do_update(
                index_elements=["suministro_id"],
                set_={
                    "nro_documento_enc": nro_documento_enc,
                    "cuit_enc": cuit_enc,
                    "actualizado_en": datetime.now(UTC),
                },
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def get(self, suministro_id: str) -> tuple[str | None, str | None] | None:
        result = await self._session.execute(
            select(
                CuentaDatosSensibles.nro_documento_enc,
                CuentaDatosSensibles.cuit_enc,
            ).where(CuentaDatosSensibles.suministro_id == suministro_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return (row[0], row[1])
