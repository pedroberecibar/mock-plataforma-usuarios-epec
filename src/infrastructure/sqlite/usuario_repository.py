from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.usuario_repository import UsuarioRepository
from infrastructure.sqlite.models import Usuario


class SQLiteUsuarioRepository(UsuarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_suministro_id(self, usuario: str) -> str | None:
        result = await self._session.execute(select(Usuario).where(Usuario.usuario == usuario))
        row = result.scalar_one_or_none()
        return row.suministro_id if row else None

    async def get_password_hash(self, usuario: str) -> str | None:
        result = await self._session.execute(select(Usuario).where(Usuario.usuario == usuario))
        row = result.scalar_one_or_none()
        return row.password_hash if row else None

    async def get_email(self, usuario: str) -> str | None:
        result = await self._session.execute(select(Usuario).where(Usuario.usuario == usuario))
        row = result.scalar_one_or_none()
        return row.email if row else None

    async def get_nombre(self, usuario: str) -> str | None:
        result = await self._session.execute(select(Usuario).where(Usuario.usuario == usuario))
        row = result.scalar_one_or_none()
        return row.nombre if row else None
