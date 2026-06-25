from domain.ports.vecinos_repository import VecinosRepository


class FakeVecinosRepository(VecinosRepository):
    def __init__(
        self,
        vecinos: dict[str, list[str]] | None = None,
        equipos: dict[str, list[str]] | None = None,
    ) -> None:
        self._vecinos = vecinos or {}
        self._equipos = equipos or {}

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        return self._vecinos.get(suministro_id, [])

    async def get_equipos_activos(self, suministro_ids: list[str]) -> list[str]:
        result: list[str] = []
        for sid in suministro_ids:
            result.extend(self._equipos.get(sid, []))
        return result
