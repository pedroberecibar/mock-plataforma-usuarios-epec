import abc


class SuministroRepository(abc.ABC):
    @abc.abstractmethod
    async def existe(self, suministro_id: str) -> bool: ...

    @abc.abstractmethod
    async def crear_placeholder(self, suministro_id: str) -> None:
        """Crea con lat=0.0, lon=0.0, suministro_referencia=suministro_id si no existe."""

    @abc.abstractmethod
    async def upsert_coordenadas(self, suministro_id: str, lat: float, lon: float) -> None:
        """Persiste coordenadas GPS. Crea el registro si no existe; actualiza si ya existe."""
