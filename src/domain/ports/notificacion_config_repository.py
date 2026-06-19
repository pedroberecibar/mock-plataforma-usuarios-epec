from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

TIPOS_ALERTA = ("factura_disponible", "vencimiento_proximo", "consumo_anomalo", "objetivo_superado")
CANAL_DEFAULT = "email"


@dataclass(frozen=True)
class NotificacionConfigEntry:
    tipo: str
    habilitado: bool


class NotificacionConfigRepository(ABC):
    @abstractmethod
    async def get_config(self, suministro_id: str) -> list[NotificacionConfigEntry]:
        """Devuelve la configuración de alertas por tipo. Si no existe, retorna todos deshabilitados."""

    @abstractmethod
    async def upsert_config(self, suministro_id: str, tipo: str, habilitado: bool) -> None:
        """Habilita o deshabilita un tipo de alerta para el suministro."""

    @abstractmethod
    async def ya_enviada_hoy(self, suministro_id: str, tipo_alerta: str, hoy: date) -> bool:
        """Devuelve True si ya se envió esta alerta hoy para este suministro."""

    @abstractmethod
    async def ya_en_cooldown(
        self, suministro_id: str, tipo_alerta: str, cooldown_horas: int, ahora: datetime
    ) -> bool:
        """Devuelve True si el último envío de este tipo fue hace menos de cooldown_horas horas."""

    @abstractmethod
    async def registrar_enviada(
        self, suministro_id: str, tipo_alerta: str, fecha_envio: datetime
    ) -> None:
        """Registra que se envió una alerta para evitar duplicados en el día."""
