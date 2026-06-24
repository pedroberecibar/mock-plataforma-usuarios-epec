"""Tests para SQLiteVecinosRepository.

En el nuevo diseño, este adapter no tiene datos de subestación y siempre devuelve [].
El criterio real (subestación) lo resuelve OracleVecinosRepository en producción.
"""

from unittest.mock import AsyncMock

from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository


async def test_retorna_lista_vacia_siempre() -> None:
    repo = SQLiteVecinosRepository(session=AsyncMock())
    assert await repo.get_vecinos("S-REF") == []


async def test_retorna_lista_vacia_para_cualquier_suministro() -> None:
    repo = SQLiteVecinosRepository(session=AsyncMock())
    assert await repo.get_vecinos("otro-id") == []
