import json
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.vecinos_cache_repository import VecinosCacheRepository


class SQLiteVecinosCacheRepository(VecinosCacheRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, suministro_id: str, vecinos: list[str]) -> None:
        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        await self._session.execute(
            text("""
                INSERT INTO vecinos_cache (suministro_id, vecinos_json, updated_at)
                VALUES (:sid, :json, :ts)
                ON CONFLICT(suministro_id) DO UPDATE
                SET vecinos_json = excluded.vecinos_json,
                    updated_at   = excluded.updated_at
            """),
            {"sid": suministro_id, "json": json.dumps(vecinos), "ts": now},
        )
