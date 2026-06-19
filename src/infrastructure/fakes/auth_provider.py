from uuid import uuid4

from domain.ports.auth_provider import AuthProvider


class FakeAuthProvider(AuthProvider):
    def __init__(self, usuarios: dict[str, str] | None = None) -> None:
        self._usuarios = usuarios or {}
        self._tokens: dict[str, str] = {}

    async def autenticar(
        self, usuario: str, password: str, password_hash: str | None = None
    ) -> str | None:
        if password_hash is not None and not self.verificar_password(password, password_hash):
            return None
        token = str(uuid4())
        self._tokens[token] = usuario
        return token

    async def verificar_token(self, token: str) -> str | None:
        return self._tokens.get(token)

    def verificar_password(self, password: str, password_hash: str) -> bool:
        return password_hash == password
