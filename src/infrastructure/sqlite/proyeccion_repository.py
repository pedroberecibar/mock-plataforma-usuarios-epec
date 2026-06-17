from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.proyeccion import ProyeccionMensual
from infrastructure.sqlite.models import ProyeccionMensual as ProyeccionMensualORM


class SQLiteProyeccionRepository(ProyeccionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_proyeccion(self, suministro_id: str, mes: date) -> ProyeccionMensual | None:
        result = await self._session.execute(
            select(ProyeccionMensualORM)
            .where(ProyeccionMensualORM.suministro_id == suministro_id)
            .where(ProyeccionMensualORM.mes == mes)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ProyeccionMensual(
            suministro_id=row.suministro_id,
            mes=row.mes,
            metodo_aplicado=row.metodo_aplicado,
            meses_usados_como_base=row.meses_usados_como_base,
            dias_usados_como_base=row.dias_usados_como_base,
            bandera_confianza=row.bandera_confianza,
            rango_inferior_kwh=row.rango_inferior_kwh,
            rango_superior_kwh=row.rango_superior_kwh,
        )

    async def upsert_proyeccion(self, proyeccion: ProyeccionMensual) -> None:
        stmt = (
            insert(ProyeccionMensualORM)
            .values(
                suministro_id=proyeccion.suministro_id,
                mes=proyeccion.mes,
                metodo_aplicado=proyeccion.metodo_aplicado,
                meses_usados_como_base=proyeccion.meses_usados_como_base,
                dias_usados_como_base=proyeccion.dias_usados_como_base,
                bandera_confianza=proyeccion.bandera_confianza,
                rango_inferior_kwh=proyeccion.rango_inferior_kwh,
                rango_superior_kwh=proyeccion.rango_superior_kwh,
            )
            .on_conflict_do_update(
                index_elements=["suministro_id", "mes"],
                set_={
                    "metodo_aplicado": proyeccion.metodo_aplicado,
                    "meses_usados_como_base": proyeccion.meses_usados_como_base,
                    "dias_usados_como_base": proyeccion.dias_usados_como_base,
                    "bandera_confianza": proyeccion.bandera_confianza,
                    "rango_inferior_kwh": proyeccion.rango_inferior_kwh,
                    "rango_superior_kwh": proyeccion.rango_superior_kwh,
                },
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()
