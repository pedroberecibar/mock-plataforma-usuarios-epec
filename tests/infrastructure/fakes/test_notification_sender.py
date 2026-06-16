from infrastructure.fakes.notification_sender import FakeNotificationSender


async def test_enviar_push_registers_the_notification() -> None:
    sender = FakeNotificationSender()

    await sender.enviar_push("U1", "Factura disponible", "Tu factura ya está disponible")

    assert sender.pushes_enviados == [("U1", "Factura disponible", "Tu factura ya está disponible")]


async def test_enviar_email_registers_the_email() -> None:
    sender = FakeNotificationSender()

    await sender.enviar_email("user@epec.com.ar", "Vencimiento próximo", "Cuerpo")

    assert sender.emails_enviados == [("user@epec.com.ar", "Vencimiento próximo", "Cuerpo")]
