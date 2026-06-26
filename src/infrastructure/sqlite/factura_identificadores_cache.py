from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.factura_identificadores import (
    FacturaIdentificadores,
    FacturaIdentificadoresCache,
)
from infrastructure.sqlite.models import FacturaRedireccion


class SQLiteFacturaIdentificadoresCache(FacturaIdentificadoresCache):
    """Cachea cliente/contrato por suministro en la tabla `factura_redireccion`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, suministro_id: str) -> FacturaIdentificadores | None:
        result = await self._session.execute(
            select(
                FacturaRedireccion.numero_cliente,
                FacturaRedireccion.numero_contrato,
            ).where(FacturaRedireccion.suministro_id == suministro_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return FacturaIdentificadores(cliente_id=row[0], contrato_id=row[1])

    async def guardar(self, suministro_id: str, ids: FacturaIdentificadores) -> None:
        stmt = (
            insert(FacturaRedireccion)
            .values(
                suministro_id=suministro_id,
                numero_cliente=ids.cliente_id,
                numero_contrato=ids.contrato_id,
            )
            .on_conflict_do_update(
                index_elements=["suministro_id"],
                set_={
                    "numero_cliente": ids.cliente_id,
                    "numero_contrato": ids.contrato_id,
                },
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
