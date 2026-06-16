from domain.ports.notification_sender import NotificationSender


class FakeNotificationSender(NotificationSender):
    def __init__(self) -> None:
        self.pushes_enviados: list[tuple[str, str, str]] = []
        self.emails_enviados: list[tuple[str, str, str]] = []

    async def enviar_push(self, usuario_id: str, titulo: str, cuerpo: str) -> None:
        self.pushes_enviados.append((usuario_id, titulo, cuerpo))

    async def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        self.emails_enviados.append((destinatario, asunto, cuerpo))
