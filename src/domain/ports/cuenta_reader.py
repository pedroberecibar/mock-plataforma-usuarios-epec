import abc

from domain.cuenta import CuentaSuministroRaw


class CuentaReader(abc.ABC):
    """Lee la metadata de cuenta de un suministro desde la fuente externa (Oracle)."""

    @abc.abstractmethod
    async def leer_cuenta(self, suministro_id: str) -> CuentaSuministroRaw | None:
        """Devuelve los datos crudos del suministro, o None si no existe."""
