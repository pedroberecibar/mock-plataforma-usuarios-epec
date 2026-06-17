from datetime import date

from domain.ports.consumo_diario_repository import ConsumoDiarioRepository


class FakeConsumoDiarioRepository(ConsumoDiarioRepository):
    def __init__(self) -> None:
        self._consumos: dict[tuple[str, date], float] = {}

    async def get_serie(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, float]]:
        return sorted(
            (fecha, kwh)
            for (sid, fecha), kwh in self._consumos.items()
            if sid == suministro_id and desde <= fecha <= hasta
        )

    async def upsert_consumo(self, suministro_id: str, fecha: date, kwh: float) -> None:
        self._consumos[(suministro_id, fecha)] = kwh

    async def get_ultima_fecha(self, suministro_id: str) -> date | None:
        fechas = [f for (sid, f) in self._consumos if sid == suministro_id]
        return max(fechas) if fechas else None
