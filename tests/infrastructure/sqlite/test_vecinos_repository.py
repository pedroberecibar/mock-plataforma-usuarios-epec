import asyncio

import pytest

from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository


def test_implements_the_port_but_methods_are_not_implemented_yet() -> None:
    repo = SQLiteVecinosRepository(session=None)

    with pytest.raises(NotImplementedError):
        asyncio.run(repo.get_vecinos("S1", 150.0))
