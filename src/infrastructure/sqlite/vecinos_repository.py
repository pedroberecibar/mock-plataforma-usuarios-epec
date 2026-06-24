from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.vecinos_repository import VecinosRepository


class SQLiteVecinosRepository(VecinosRepository):
    """Fallback de desarrollo: sin datos de subestación en SQLite, retorna vacío.

    En producción el adapter Oracle es el que se usa.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        return []
