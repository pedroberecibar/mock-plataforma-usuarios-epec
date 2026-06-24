"""Adapter SQLite que agrega un cache TTL sobre cualquier VecinosRepository.

Los vecinos de un suministro cambian raramente (zonas geográficas EPEC estables).
Este adapter guarda el resultado en la tabla vecinos_cache y lo sirve desde SQLite
en las siguientes requests, evitando el round-trip a Oracle en cada /home.
"""

import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.vecinos_repository import VecinosRepository
from infrastructure.sqlite.models import VecinosCache


class CachedVecinosRepository(VecinosRepository):
    _DEFAULT_TTL_HOURS = 24

    def __init__(
        self,
        inner: VecinosRepository,
        session: AsyncSession,
        *,
        ttl_hours: int = _DEFAULT_TTL_HOURS,
    ) -> None:
        self._inner = inner
        self._session = session
        self._ttl_seconds = ttl_hours * 3600

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        cached = await self._get_from_cache(suministro_id)
        if cached is not None:
            return cached

        try:
            vecinos = await self._inner.get_vecinos(suministro_id)
        except Exception:
            return []

        if vecinos:
            await self._save_to_cache(suministro_id, vecinos)
        return vecinos

    async def _get_from_cache(self, suministro_id: str) -> list[str] | None:
        result = await self._session.execute(
            select(VecinosCache).where(VecinosCache.suministro_id == suministro_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        age = (datetime.now(UTC).replace(tzinfo=None) - row.updated_at).total_seconds()
        if age >= self._ttl_seconds:
            return None

        return json.loads(row.vecinos_json)  # type: ignore[no-any-return]

    async def _save_to_cache(self, suministro_id: str, vecinos: list[str]) -> None:
        stmt = (
            insert(VecinosCache)
            .values(
                suministro_id=suministro_id,
                vecinos_json=json.dumps(vecinos),
                updated_at=datetime.now(UTC).replace(tzinfo=None),
            )
            .on_conflict_do_update(
                index_elements=["suministro_id"],
                set_={
                    "vecinos_json": json.dumps(vecinos),
                    "updated_at": datetime.now(UTC).replace(tzinfo=None),
                },
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
