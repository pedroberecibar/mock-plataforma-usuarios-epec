from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from domain.ports.auth_provider import AuthProvider
from domain.ports.usuario_repository import UsuarioRepository
from interface.dependencies import get_auth_provider, get_usuario_repo

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    token: str
    suministro_id: str


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    auth_provider: AuthProvider = Depends(get_auth_provider),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
) -> LoginResponse:
    suministro_id = await usuario_repo.get_suministro_id(body.usuario)
    if suministro_id is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = await auth_provider.autenticar(body.usuario, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return LoginResponse(token=token, suministro_id=suministro_id)
