from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from domain.ports.auth_provider import AuthProvider
from interface.dependencies import get_auth_provider

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest, auth_provider: AuthProvider = Depends(get_auth_provider)
) -> LoginResponse:
    token = await auth_provider.autenticar(body.usuario, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return LoginResponse(token=token)
