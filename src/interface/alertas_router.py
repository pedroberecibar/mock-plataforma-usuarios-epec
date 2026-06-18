from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from domain.ports.notificacion_config_repository import (
    TIPOS_ALERTA,
    NotificacionConfigRepository,
)
from interface.dependencies import get_notificacion_config_repo, get_suministro_actual

router = APIRouter(prefix="/alertas", tags=["alertas"])


class AlertaConfigItem(BaseModel):
    tipo: str
    habilitado: bool


class PatchAlertaConfigBody(BaseModel):
    tipo: str
    habilitado: bool

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        if v not in TIPOS_ALERTA:
            raise ValueError(f"Tipo de alerta inválido: {v}. Válidos: {TIPOS_ALERTA}")
        return v


@router.get("/config", response_model=list[AlertaConfigItem])
async def get_config(
    suministro_id: str = Depends(get_suministro_actual),
    repo: NotificacionConfigRepository = Depends(get_notificacion_config_repo),
) -> list[AlertaConfigItem]:
    entries = await repo.get_config(suministro_id)
    return [AlertaConfigItem(tipo=e.tipo, habilitado=e.habilitado) for e in entries]


@router.patch("/config", response_model=AlertaConfigItem)
async def patch_config(
    body: PatchAlertaConfigBody,
    suministro_id: str = Depends(get_suministro_actual),
    repo: NotificacionConfigRepository = Depends(get_notificacion_config_repo),
) -> AlertaConfigItem:
    await repo.upsert_config(suministro_id, body.tipo, body.habilitado)
    return AlertaConfigItem(tipo=body.tipo, habilitado=body.habilitado)
