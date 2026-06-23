from datetime import date

from application.use_cases.evaluar_alertas import EvaluarAlertasUseCase, TipoAlerta
from domain.ports.factura_source_reader import FacturaSourceReader
from domain.ports.notificacion_config_repository import NotificacionConfigRepository
from domain.ports.notification_sender import NotificationSender

_UMBRAL_DIAS = 5


class EvaluarVencimientoUseCase:
    def __init__(
        self,
        factura_reader: FacturaSourceReader,
        notificacion_repo: NotificacionConfigRepository,
        notification_sender: NotificationSender,
    ) -> None:
        self._factura_reader = factura_reader
        self._notificacion_repo = notificacion_repo
        self._notification_sender = notification_sender

    async def ejecutar(
        self,
        suministro_id: str,
        email: str,
        hoy: date | None = None,
    ) -> None:
        from datetime import UTC, datetime

        if hoy is not None:
            ahora_real = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
            hoy_real = hoy
        else:
            ahora_real = datetime.now(UTC).replace(tzinfo=None)
            hoy_real = ahora_real.date()

        factura = await self._factura_reader.get_factura(suministro_id)
        if factura is None or factura.fecha_vencimiento is None:
            return

        dias_restantes = (factura.fecha_vencimiento - hoy_real).days
        if dias_restantes > _UMBRAL_DIAS:
            return

        evaluar_alertas = EvaluarAlertasUseCase(
            notificacion_repo=self._notificacion_repo,
            notification_sender=self._notification_sender,
            email_destinatario=email,
        )
        await evaluar_alertas.ejecutar(
            suministro_id=suministro_id,
            tipos=[TipoAlerta.VENCIMIENTO_PROXIMO],
            hoy=hoy_real,
            ahora=ahora_real,
        )
