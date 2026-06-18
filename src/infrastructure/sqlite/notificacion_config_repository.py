from datetime import date, datetime

from sqlalchemy import select, text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.notificacion_config_repository import (
    CANAL_DEFAULT,
    TIPOS_ALERTA,
    NotificacionConfigEntry,
    NotificacionConfigRepository,
)
from infrastructure.sqlite.models import NotificacionConfig, NotificacionEnviada


class SQLiteNotificacionConfigRepository(NotificacionConfigRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_config(self, suministro_id: str) -> list[NotificacionConfigEntry]:
        result = await self._session.execute(
            select(NotificacionConfig).where(
                NotificacionConfig.usuario_id == suministro_id,
                NotificacionConfig.canal == CANAL_DEFAULT,
            )
        )
        rows = {row.tipo: row.habilitado for row in result.scalars()}
        return [
            NotificacionConfigEntry(tipo=tipo, habilitado=rows.get(tipo, False))
            for tipo in TIPOS_ALERTA
        ]

    async def upsert_config(self, suministro_id: str, tipo: str, habilitado: bool) -> None:
        stmt = sqlite_insert(NotificacionConfig).values(
            usuario_id=suministro_id,
            tipo=tipo,
            canal=CANAL_DEFAULT,
            habilitado=habilitado,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["usuario_id", "tipo", "canal"],
            set_={"habilitado": habilitado},
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def ya_enviada_hoy(self, suministro_id: str, tipo_alerta: str, hoy: date) -> bool:
        result = await self._session.execute(
            select(NotificacionEnviada)
            .where(
                NotificacionEnviada.suministro_id == suministro_id,
                NotificacionEnviada.tipo_alerta == tipo_alerta,
                text("DATE(notificaciones_enviadas.fecha_envio) = :hoy"),
            )
            .params(hoy=hoy.isoformat())
        )
        return result.scalar_one_or_none() is not None

    async def registrar_enviada(
        self, suministro_id: str, tipo_alerta: str, fecha_envio: datetime
    ) -> None:
        self._session.add(
            NotificacionEnviada(
                suministro_id=suministro_id,
                tipo_alerta=tipo_alerta,
                fecha_envio=fecha_envio,
            )
        )
        await self._session.flush()
