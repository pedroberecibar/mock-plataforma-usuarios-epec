from domain.ports.suministro_repository import SuministroRepository


class FakeSuministroRepository(SuministroRepository):
    def __init__(self) -> None:
        self._suministros: set[str] = set()
        self._coordenadas: dict[str, tuple[float, float]] = {}

    async def existe(self, suministro_id: str) -> bool:
        return suministro_id in self._suministros

    async def crear_placeholder(self, suministro_id: str) -> None:
        self._suministros.add(suministro_id)

    async def upsert_coordenadas(self, suministro_id: str, lat: float, lon: float) -> None:
        self._suministros.add(suministro_id)
        self._coordenadas[suministro_id] = (lat, lon)
