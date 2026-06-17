from fastapi import Depends, Header, HTTPException

from domain.ports.auth_provider import AuthProvider
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError("AuthProvider debe ser wireado en el composition root (src/main.py)")


def get_consumo_repo() -> ConsumoDiarioRepository:
    raise NotImplementedError(
        "ConsumoDiarioRepository debe ser wireado en el composition root (src/main.py)"
    )


async def get_usuario_actual(
    authorization: str | None = Header(None),
    auth_provider: AuthProvider = Depends(get_auth_provider),
) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token ausente")
    usuario = await auth_provider.verificar_token(authorization)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario
