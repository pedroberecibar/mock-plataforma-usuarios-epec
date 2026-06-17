from fastapi import Depends, Header, HTTPException

from domain.ports.auth_provider import AuthProvider
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.ports.suministro_repository import SuministroRepository
from domain.ports.vecinos_repository import VecinosRepository


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError("AuthProvider debe ser wireado en el composition root (src/main.py)")


def get_consumo_repo() -> ConsumoDiarioRepository:
    raise NotImplementedError(
        "ConsumoDiarioRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_vecinos_repo() -> VecinosRepository:
    raise NotImplementedError(
        "VecinosRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_proyeccion_repo() -> ProyeccionRepository:
    raise NotImplementedError(
        "ProyeccionRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_medicion_reader() -> MedicionSourceReader:
    raise NotImplementedError(
        "MedicionSourceReader debe ser wireado en el composition root (src/main.py)"
    )


def get_suministro_repo() -> SuministroRepository:
    raise NotImplementedError(
        "SuministroRepository debe ser wireado en el composition root (src/main.py)"
    )


async def get_usuario_actual(
    authorization: str | None = Header(None),
    auth_provider: AuthProvider = Depends(get_auth_provider),
) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.removeprefix("Bearer ").strip()
    usuario = await auth_provider.verificar_token(token)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return usuario
