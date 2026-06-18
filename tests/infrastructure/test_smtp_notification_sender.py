"""Tests para SmtpNotificationSender con mock de aiosmtplib.send."""

from email.mime.text import MIMEText
from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.smtp.notification_sender import SmtpNotificationSender


@pytest.fixture
def sender() -> SmtpNotificationSender:
    return SmtpNotificationSender(
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass",
        from_addr="alertas@epec.com.ar",
        use_tls=False,
    )


async def test_enviar_email_llama_a_aiosmtplib_send(sender: SmtpNotificationSender) -> None:
    with patch(
        "infrastructure.smtp.notification_sender.aiosmtplib.send",
        new_callable=AsyncMock,
    ) as mock_send:
        await sender.enviar_email(
            destinatario="cliente@example.com",
            asunto="Factura disponible",
            cuerpo="Tu factura de junio ya está disponible.",
        )

    mock_send.assert_called_once()
    kwargs = mock_send.call_args.kwargs
    assert kwargs["hostname"] == "smtp.example.com"
    assert kwargs["port"] == 587


async def test_enviar_email_incluye_asunto_y_destinatario(sender: SmtpNotificationSender) -> None:
    with patch(
        "infrastructure.smtp.notification_sender.aiosmtplib.send",
        new_callable=AsyncMock,
    ) as mock_send:
        await sender.enviar_email(
            destinatario="pedro@example.com",
            asunto="Vencimiento próximo",
            cuerpo="Tu factura vence en 3 días.",
        )

    msg: MIMEText = mock_send.call_args.args[0]
    assert msg["Subject"] == "Vencimiento próximo"
    assert msg["To"] == "pedro@example.com"
    assert msg["From"] == "alertas@epec.com.ar"


async def test_enviar_push_es_noop_sin_excepcion(sender: SmtpNotificationSender) -> None:
    # En MVP, push es no-op; no debe lanzar excepción
    await sender.enviar_push(
        usuario_id="SRV-001",
        titulo="Test push",
        cuerpo="Cuerpo de prueba",
    )
