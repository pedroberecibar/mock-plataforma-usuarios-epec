from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from domain.ports.auth_provider import AuthProvider

ALGORITHM = "HS256"
EXPIRACION = timedelta(hours=12)

_ph = PasswordHasher()


class JwtAuthProvider(AuthProvider):
    """Emite y verifica JWTs. La verificación de contraseña usa argon2id."""

    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key

    async def autenticar(
        self, usuario: str, password: str, password_hash: str | None = None
    ) -> str | None:
        if password_hash is not None and not self.verificar_password(password, password_hash):
            return None
        payload = {"sub": usuario, "exp": datetime.now(UTC) + EXPIRACION}
        return jwt.encode(payload, self._secret_key, algorithm=ALGORITHM)

    async def verificar_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            return None
        return payload.get("sub")

    def verificar_password(self, password: str, password_hash: str) -> bool:
        try:
            return _ph.verify(password_hash, password)
        except VerifyMismatchError:
            return False
