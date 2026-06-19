from datetime import UTC, date, datetime
from enum import StrEnum

from domain.ports.notificacion_config_repository import NotificacionConfigRepository
from domain.ports.notification_sender import NotificationSender

ASUNTOS: dict[str, str] = {
    "factura_disponible": "Tu factura EPEC ya está disponible",
    "vencimiento_proximo": "Tu factura EPEC vence pronto",
    "consumo_anomalo": "Alerta: consumo inusual detectado",
    "objetivo_superado": "Alerta: tu objetivo de consumo está por alcanzarse",
}

CUERPOS: dict[str, str] = {
    "factura_disponible": (
        "Tu nueva factura de EPEC está disponible. Ingresá a la plataforma para verla y abonarla."
    ),
    "vencimiento_proximo": (
        "Tu factura EPEC vence en los próximos días. Recordá abonarla para evitar inconvenientes."
    ),
    "consumo_anomalo": (
        "Detectamos un consumo fuera de lo habitual en tu suministro. "
        "Revisá el detalle en la sección Consumo."
    ),
    "objetivo_superado": (
        "Tu consumo acumulado este mes alcanzó el límite configurado. "
        "Ingresá a la plataforma para revisar el detalle y ajustar tu objetivo si es necesario."
    ),
}


_COOLDOWN_HORAS: dict[str, int] = {
    "factura_disponible": 24,
    "vencimiento_proximo": 24,
    "objetivo_superado": 12,
    "consumo_anomalo": 6,
}


class TipoAlerta(StrEnum):
    FACTURA_DISPONIBLE = "factura_disponible"
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"
    CONSUMO_ANOMALO = "consumo_anomalo"
    OBJETIVO_SUPERADO = "objetivo_superado"


class EvaluarAlertasUseCase:
    def __init__(
        self,
        notificacion_repo: NotificacionConfigRepository,
        notification_sender: NotificationSender,
        email_destinatario: str,
    ) -> None:
        self._notificacion_repo = notificacion_repo
        self._sender = notification_sender
        self._email_destinatario = email_destinatario

    async def ejecutar(
        self,
        suministro_id: str,
        tipos: list[TipoAlerta],
        hoy: date | None = None,
        ahora: datetime | None = None,
    ) -> None:
        if ahora is None:
            ahora = datetime.now(UTC).replace(tzinfo=None)
        if hoy is None:
            hoy = ahora.date()

        config_list = await self._notificacion_repo.get_config(suministro_id)
        config = {c.tipo: c.habilitado for c in config_list}

        for tipo in tipos:
            tipo_str = str(tipo)
            if not config.get(tipo_str, False):
                continue
            cooldown = _COOLDOWN_HORAS.get(tipo_str, 24)
            if await self._notificacion_repo.ya_en_cooldown(
                suministro_id, tipo_str, cooldown, ahora
            ):
                continue

            await self._sender.enviar_email(
                destinatario=self._email_destinatario,
                asunto=ASUNTOS[tipo_str],
                cuerpo=CUERPOS[tipo_str],
            )
            await self._notificacion_repo.registrar_enviada(suministro_id, tipo_str, ahora)
