from abc import ABC, abstractmethod


class UsuarioRepository(ABC):
    @abstractmethod
    async def get_suministro_id(self, usuario: str) -> str | None:
        """Devuelve el suministro_id asociado al usuario, o None si no existe."""
