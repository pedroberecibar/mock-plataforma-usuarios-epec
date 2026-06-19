from abc import ABC, abstractmethod


class AuthProvider(ABC):
    @abstractmethod
    async def autenticar(
        self, usuario: str, password: str, password_hash: str | None = None
    ) -> str | None:
        """Genera token si la contraseña coincide con el hash (o si no hay hash configurado)."""

    @abstractmethod
    async def verificar_token(self, token: str) -> str | None:
        """Verifica un token y devuelve el id de usuario, o None si es inválido."""

    @abstractmethod
    def verificar_password(self, password: str, password_hash: str) -> bool:
        """Verifica que la contraseña en texto plano coincide con el hash almacenado."""
