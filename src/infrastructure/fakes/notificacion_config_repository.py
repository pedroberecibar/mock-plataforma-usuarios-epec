from datetime import date, datetime, timedelta

from domain.ports.notificacion_config_repository import (
    TIPOS_ALERTA,
    NotificacionConfigEntry,
    NotificacionConfigRepository,
)


class FakeNotificacionConfigRepository(NotificacionConfigRepository):
    def __init__(self) -> None:
        self._config: dict[tuple[str, str], bool] = {}
        self._enviadas: list[tuple[str, str, datetime]] = []

    async def get_config(self, suministro_id: str) -> list[NotificacionConfigEntry]:
        return [
            NotificacionConfigEntry(
                tipo=tipo,
                habilitado=self._config.get((suministro_id, tipo), False),
            )
            for tipo in TIPOS_ALERTA
        ]

    async def upsert_config(self, suministro_id: str, tipo: str, habilitado: bool) -> None:
        self._config[(suministro_id, tipo)] = habilitado

    async def ya_enviada_hoy(self, suministro_id: str, tipo_alerta: str, hoy: date) -> bool:
        return any(
            sid == suministro_id and tipo == tipo_alerta and ts.date() == hoy
            for sid, tipo, ts in self._enviadas
        )

    async def ya_en_cooldown(
        self, suministro_id: str, tipo_alerta: str, cooldown_horas: int, ahora: datetime
    ) -> bool:
        limite = ahora - timedelta(hours=cooldown_horas)
        return any(
            sid == suministro_id and tipo == tipo_alerta and ts >= limite
            for sid, tipo, ts in self._enviadas
        )

    async def registrar_enviada(
        self, suministro_id: str, tipo_alerta: str, fecha_envio: datetime
    ) -> None:
        self._enviadas.append((suministro_id, tipo_alerta, fecha_envio))
