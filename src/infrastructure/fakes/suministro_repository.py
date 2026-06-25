from domain.ports.suministro_repository import SuministroRepository


class FakeSuministroRepository(SuministroRepository):
    def __init__(self) -> None:
        self._suministros: set[str] = set()
        self._coordenadas: dict[str, tuple[float, float]] = {}
        self._tarifas: dict[str, str] = {}

    async def existe(self, suministro_id: str) -> bool:
        return suministro_id in self._suministros

    async def crear_placeholder(self, suministro_id: str) -> None:
        self._suministros.add(suministro_id)

    async def upsert_coordenadas(self, suministro_id: str, lat: float, lon: float) -> None:
        self._suministros.add(suministro_id)
        self._coordenadas[suministro_id] = (lat, lon)

    async def get_tarifa_codigo(self, suministro_id: str) -> str | None:
        return self._tarifas.get(suministro_id)

    async def upsert_tarifa(self, suministro_id: str, tarifa_codigo: str) -> None:
        self._suministros.add(suministro_id)
        self._tarifas[suministro_id] = tarifa_codigo
