import asyncio
from datetime import date

import pytest

from infrastructure.sqlite.objetivo_consumo_repository import SQLiteObjetivoConsumoRepository


def test_implements_the_port_but_methods_are_not_implemented_yet() -> None:
    repo = SQLiteObjetivoConsumoRepository(session=None)

    with pytest.raises(NotImplementedError):
        asyncio.run(repo.get_vigente("S1"))

    with pytest.raises(NotImplementedError):
        asyncio.run(repo.upsert_objetivo("S1", 150.0, "sugerido", date(2026, 1, 1)))
