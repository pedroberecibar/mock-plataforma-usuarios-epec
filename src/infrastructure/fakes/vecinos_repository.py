from domain.ports.vecinos_repository import VecinosRepository


class FakeVecinosRepository(VecinosRepository):
    def __init__(self, vecinos: dict[str, list[str]] | None = None) -> None:
        self._vecinos = vecinos or {}

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        return self._vecinos.get(suministro_id, [])
