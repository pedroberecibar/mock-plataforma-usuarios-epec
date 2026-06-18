from abc import ABC, abstractmethod


class UsuarioRepository(ABC):
    @abstractmethod
    async def get_suministro_id(self, usuario: str) -> str | None:
        """Devuelve el suministro_id asociado al usuario, o None si no existe."""

    @abstractmethod
    async def get_password_hash(self, usuario: str) -> str | None:
        """Devuelve el password_hash almacenado para el usuario, o None si no existe."""
