from abc import ABC, abstractmethod


class VecinosRepository(ABC):
    @abstractmethod
    async def get_vecinos(self, suministro_id: str) -> list[str]:
        """Devuelve los ids de suministros de la misma subestación, excluyendo el propio."""

    @abstractmethod
    async def get_equipos_activos(self, suministro_ids: list[str]) -> list[str]:
        """Dado SRV_CODIGOs canónicos, devuelve los med_numero_equipo activos y telemedibles."""
