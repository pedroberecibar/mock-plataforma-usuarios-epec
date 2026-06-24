from abc import ABC, abstractmethod


class VecinosRepository(ABC):
    @abstractmethod
    async def get_vecinos(self, suministro_id: str) -> list[str]:
        """Devuelve los ids de suministros de la misma subestación, excluyendo el propio."""
