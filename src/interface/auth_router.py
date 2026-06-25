from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from domain.ports.auth_provider import AuthProvider
from domain.ports.suministro_repository import SuministroRepository
from domain.ports.usuario_repository import UsuarioRepository
from interface.dependencies import (
    get_auth_provider,
    get_suministro_actual,
    get_suministro_repo,
    get_usuario_actual,
    get_usuario_repo,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    token: str
    suministro_id: str
    nombre: str | None
    nro_suministro: str


class PerfilResponse(BaseModel):
    nombre: str | None
    nro_suministro: str
    suministro_id: str
    tarifa_codigo: str | None


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    auth_provider: AuthProvider = Depends(get_auth_provider),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
) -> LoginResponse:
    suministro_id = await usuario_repo.get_suministro_id(body.usuario)
    if suministro_id is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    password_hash = await usuario_repo.get_password_hash(body.usuario)
    if password_hash is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = await auth_provider.autenticar(body.usuario, body.password, password_hash)
    if token is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    nombre = await usuario_repo.get_nombre(body.usuario)
    return LoginResponse(
        token=token,
        suministro_id=suministro_id,
        nombre=nombre,
        nro_suministro=body.usuario,
    )


@router.get("/me", response_model=PerfilResponse)
async def get_me(
    usuario: str = Depends(get_usuario_actual),
    suministro_id: str = Depends(get_suministro_actual),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
    suministro_repo: SuministroRepository = Depends(get_suministro_repo),
) -> PerfilResponse:
    nombre = await usuario_repo.get_nombre(usuario)
    tarifa_codigo = await suministro_repo.get_tarifa_codigo(suministro_id)
    return PerfilResponse(
        nombre=nombre,
        nro_suministro=usuario,
        suministro_id=suministro_id,
        tarifa_codigo=tarifa_codigo,
    )
