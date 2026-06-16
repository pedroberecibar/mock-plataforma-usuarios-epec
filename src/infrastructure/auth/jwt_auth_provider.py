from datetime import UTC, datetime, timedelta

import jwt

from domain.ports.auth_provider import AuthProvider

ALGORITHM = "HS256"
EXPIRACION = timedelta(hours=12)


class JwtAuthProvider(AuthProvider):
    """Login stub: emite un JWT para cualquier credencial.

    La verificación real de identidad contra EPEC es un punto abierto
    (ver docs/PLAN-SPRINTS-MVP.md, riesgo #2); por ahora solo garantiza
    que el token emitido y verificado en esta plataforma sea consistente.
    """

    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key

    async def autenticar(self, usuario: str, password: str) -> str | None:
        payload = {"sub": usuario, "exp": datetime.now(UTC) + EXPIRACION}
        return jwt.encode(payload, self._secret_key, algorithm=ALGORITHM)

    async def verificar_token(self, token: str) -> str | None:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            return None
        return payload.get("sub")
