from abc import ABC, abstractmethod
from datetime import date

from domain.proyeccion import ProyeccionMensual


class ProyeccionRepository(ABC):
    @abstractmethod
    async def get_proyeccion(self, suministro_id: str, mes: date) -> ProyeccionMensual | None:
        """Devuelve la proyeccion mensual para el suministro y mes; None si no existe."""

    @abstractmethod
    async def upsert_proyeccion(self, proyeccion: ProyeccionMensual) -> None:
        """Inserta o actualiza la proyeccion mensual."""
