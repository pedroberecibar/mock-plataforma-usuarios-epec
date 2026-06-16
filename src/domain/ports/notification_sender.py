from abc import ABC, abstractmethod


class NotificationSender(ABC):
    @abstractmethod
    async def enviar_push(self, usuario_id: str, titulo: str, cuerpo: str) -> None:
        """Envía una notificación push web al usuario indicado."""

    @abstractmethod
    async def enviar_email(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        """Envía un email transaccional al destinatario indicado."""
