from abc import ABC, abstractmethod


class VecinosRepository(ABC):
    @abstractmethod
    async def get_vecinos(self, suministro_id: str, radio_metros: float) -> list[str]:
        """Devuelve los ids de suministros dentro del radio dado, excluyendo el propio."""
