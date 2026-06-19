from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from application.use_cases.evaluar_alertas import EvaluarAlertasUseCase
from application.use_cases.evaluar_objetivo_consumo import EvaluarObjetivoConsumoUseCase
from application.use_cases.evaluar_vencimiento import EvaluarVencimientoUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.factura_source_reader import FacturaSourceReader
from domain.ports.notificacion_config_repository import (
    TIPOS_ALERTA,
    NotificacionConfigRepository,
)
from domain.ports.notification_sender import NotificationSender
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from interface.dependencies import (
    get_consumo_repo,
    get_email_actual,
    get_factura_reader,
    get_notificacion_config_repo,
    get_notification_sender,
    get_objetivo_repo,
    get_suministro_actual,
)

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


class EvaluarObjetivoResponse(BaseModel):
    evaluado: bool
    mensaje: str


@router.post("/evaluar-objetivo", response_model=EvaluarObjetivoResponse)
async def evaluar_objetivo(
    suministro_id: str = Depends(get_suministro_actual),
    email: str | None = Depends(get_email_actual),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
    objetivo_repo: ObjetivoConsumoRepository = Depends(get_objetivo_repo),
    notif_repo: NotificacionConfigRepository = Depends(get_notificacion_config_repo),
    notification_sender: NotificationSender = Depends(get_notification_sender),
) -> EvaluarObjetivoResponse:
    email_destino = email or f"{suministro_id}@epec.com.ar"
    evaluar_alertas_uc = EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=notification_sender,
        email_destinatario=email_destino,
    )
    uc = EvaluarObjetivoConsumoUseCase(
        consumo_repo=consumo_repo,
        objetivo_repo=objetivo_repo,
        evaluar_alertas=evaluar_alertas_uc,
    )
    hoy = datetime.now(UTC).date()
    mes = hoy.replace(day=1)
    await uc.ejecutar(suministro_id, mes, hoy=hoy)
    return EvaluarObjetivoResponse(evaluado=True, mensaje="Objetivo evaluado correctamente")


class EvaluarVencimientoResponse(BaseModel):
    evaluado: bool
    mensaje: str


@router.post("/evaluar-vencimiento", response_model=EvaluarVencimientoResponse)
async def evaluar_vencimiento(
    suministro_id: str = Depends(get_suministro_actual),
    email: str | None = Depends(get_email_actual),
    factura_reader: FacturaSourceReader = Depends(get_factura_reader),
    notif_repo: NotificacionConfigRepository = Depends(get_notificacion_config_repo),
    notification_sender: NotificationSender = Depends(get_notification_sender),
) -> EvaluarVencimientoResponse:
    email_destino = email or f"{suministro_id}@epec.com.ar"
    uc = EvaluarVencimientoUseCase(
        factura_reader=factura_reader,
        notificacion_repo=notif_repo,
        notification_sender=notification_sender,
    )
    hoy = datetime.now(UTC).date()
    await uc.ejecutar(suministro_id, email=email_destino, hoy=hoy)
    return EvaluarVencimientoResponse(evaluado=True, mensaje="Vencimiento evaluado correctamente")
