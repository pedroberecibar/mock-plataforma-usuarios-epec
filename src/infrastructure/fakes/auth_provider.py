from uuid import uuid4

from domain.ports.auth_provider import AuthProvider


class FakeAuthProvider(AuthProvider):
    def __init__(self, usuarios: dict[str, str] | None = None) -> None:
        self._usuarios = usuarios or {}
        self._tokens: dict[str, str] = {}

    async def autenticar(self, usuario: str, password: str) -> str | None:
        if self._usuarios.get(usuario) != password:
            return None
        token = str(uuid4())
        self._tokens[token] = usuario
        return token

    async def verificar_token(self, token: str) -> str | None:
        return self._tokens.get(token)
