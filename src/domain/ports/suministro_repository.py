import abc


class SuministroRepository(abc.ABC):
    @abc.abstractmethod
    async def existe(self, suministro_id: str) -> bool: ...

    @abc.abstractmethod
    async def crear_placeholder(self, suministro_id: str) -> None:
        """Crea con lat=0.0, lon=0.0, suministro_referencia=suministro_id si no existe."""
