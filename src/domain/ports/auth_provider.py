from abc import ABC, abstractmethod


class AuthProvider(ABC):
    @abstractmethod
    async def autenticar(self, usuario: str, password: str) -> str | None:
        """Verifica credenciales y devuelve un token de sesión, o None si son inválidas."""

    @abstractmethod
    async def verificar_token(self, token: str) -> str | None:
        """Verifica un token y devuelve el id de usuario, o None si es inválido."""
