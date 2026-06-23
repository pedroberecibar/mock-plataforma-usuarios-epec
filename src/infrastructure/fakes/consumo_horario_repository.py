from datetime import date

from domain.ports.consumo_horario_repository import ConsumoHorarioRepository


class FakeConsumoHorarioRepository(ConsumoHorarioRepository):
    def __init__(self) -> None:
        self._consumos: dict[tuple[str, date, int], float] = {}

    async def get_serie_horaria(self, suministro_id: str, fecha: date) -> list[tuple[int, float]]:
        return sorted(
            (hora, kwh)
            for (sid, f, hora), kwh in self._consumos.items()
            if sid == suministro_id and f == fecha
        )

    async def upsert_consumo_horario(
        self, suministro_id: str, fecha: date, hora: int, kwh: float
    ) -> None:
        self._consumos[(suministro_id, fecha, hora)] = kwh

    async def get_ultima_fecha_horaria(self, suministro_id: str) -> date | None:
        fechas = [f for (sid, f, _) in self._consumos if sid == suministro_id]
        return max(fechas) if fechas else None

    async def get_serie_horaria_rango(
        self, suministro_id: str, desde: date, hasta: date
    ) -> list[tuple[date, int, float]]:
        return sorted(
            (f, hora, kwh)
            for (sid, f, hora), kwh in self._consumos.items()
            if sid == suministro_id and desde <= f <= hasta
        )
