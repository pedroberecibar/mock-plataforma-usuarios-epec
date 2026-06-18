from abc import ABC, abstractmethod


class AuthProvider(ABC):
    @abstractmethod
    async def autenticar(self, usuario: str, password: str) -> str | None:
        """Genera un token de sesión para el usuario dado. No verifica contraseña."""

    @abstractmethod
    async def verificar_token(self, token: str) -> str | None:
        """Verifica un token y devuelve el id de usuario, o None si es inválido."""

    @abstractmethod
    def verificar_password(self, password: str, password_hash: str) -> bool:
        """Verifica que la contraseña en texto plano coincide con el hash almacenado."""
