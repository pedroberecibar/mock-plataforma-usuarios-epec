import logging
from email.mime.text import MIMEText

import aiosmtplib

from domain.ports.notification_sender import NotificationSender

log = logging.getLogger(__name__)


class SmtpNotificationSender(NotificationSender):
    """Envía alertas por email vía SMTP. Push no implementado en MVP (no-op)."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        from_addr: str,
        use_tls: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_addr = from_addr
        self._use_tls = use_tls

    async def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        msg = MIMEText(cuerpo, "plain", "utf-8")
        msg["Subject"] = asunto
        msg["From"] = self._from_addr
        msg["To"] = destinatario

        await aiosmtplib.send(
            msg,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
        )
        log.info("Email enviado a %s — %s", destinatario, asunto)

    async def enviar_push(self, usuario_id: str, titulo: str, cuerpo: str) -> None:
        log.debug("Push no implementado en MVP — ignorado para usuario %s", usuario_id)
