from fastapi import Depends, Header, HTTPException

from domain.ports.auth_provider import AuthProvider
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.consumo_horario_repository import ConsumoHorarioRepository
from domain.ports.cuenta_reader import CuentaReader
from domain.ports.cuenta_sensible_repository import CuentaSensibleRepository
from domain.ports.factura_source_reader import FacturaSourceReader
from domain.ports.factura_verificacion_port import FacturaVerificacionPort
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.notificacion_config_repository import NotificacionConfigRepository
from domain.ports.notification_sender import NotificationSender
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from domain.ports.pii_cipher import PiiCipher
from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.ports.suministro_repository import SuministroRepository
from domain.ports.usuario_repository import UsuarioRepository
from domain.ports.vecinos_repository import VecinosRepository


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError("AuthProvider debe ser wireado en el composition root (src/main.py)")


def get_usuario_repo() -> UsuarioRepository:
    raise NotImplementedError(
        "UsuarioRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_notificacion_config_repo() -> NotificacionConfigRepository:
    raise NotImplementedError(
        "NotificacionConfigRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_consumo_repo() -> ConsumoDiarioRepository:
    raise NotImplementedError(
        "ConsumoDiarioRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_consumo_horario_repo() -> ConsumoHorarioRepository:
    raise NotImplementedError(
        "ConsumoHorarioRepository debe ser wireado en el composition root (src/main.py)"
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


def get_objetivo_repo() -> ObjetivoConsumoRepository:
    raise NotImplementedError(
        "ObjetivoConsumoRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_cuenta_reader() -> CuentaReader:
    raise NotImplementedError("CuentaReader debe ser wireado en el composition root (src/main.py)")


def get_pii_cipher() -> PiiCipher:
    raise NotImplementedError("PiiCipher debe ser wireado en el composition root (src/main.py)")


def get_cuenta_sensible_repo() -> CuentaSensibleRepository:
    raise NotImplementedError(
        "CuentaSensibleRepository debe ser wireado en el composition root (src/main.py)"
    )


def get_notification_sender() -> NotificationSender:
    raise NotImplementedError(
        "NotificationSender debe ser wireado en el composition root (src/main.py)"
    )


def get_factura_reader() -> FacturaSourceReader:
    raise NotImplementedError(
        "FacturaSourceReader debe ser wireado en el composition root (src/main.py)"
    )


def get_factura_verificacion() -> FacturaVerificacionPort:
    raise NotImplementedError(
        "FacturaVerificacionPort debe ser wireado en el composition root (src/main.py)"
    )


def get_poblar_use_case() -> object:
    raise NotImplementedError(
        "PoblarSuministroUseCase debe ser wireado en el composition root (src/main.py)"
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


async def get_suministro_actual(
    usuario: str = Depends(get_usuario_actual),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
) -> str:
    suministro_id = await usuario_repo.get_suministro_id(usuario)
    if suministro_id is None:
        raise HTTPException(status_code=401, detail="Usuario sin suministro asignado")
    return suministro_id


async def get_email_actual(
    usuario: str = Depends(get_usuario_actual),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
) -> str | None:
    return await usuario_repo.get_email(usuario)
