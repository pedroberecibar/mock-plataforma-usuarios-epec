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

    async def get_serie_promedio_zona(
        self, vecino_ids: list[str], desde: date, hasta: date
    ) -> list[tuple[date, float]]:
        from collections import defaultdict

        totales: dict[date, list[float]] = defaultdict(list)
        for (sid, fecha), kwh in self._consumos.items():
            if sid in vecino_ids and desde <= fecha <= hasta:
                totales[fecha].append(kwh)
        return sorted(
            (fecha, round(sum(vals) / len(vals), 2)) for fecha, vals in totales.items() if vals
        )

    async def get_totales_por_suministro(
        self, suministro_ids: list[str], desde: date, hasta: date
    ) -> list[tuple[str, float]]:
        ids_set = set(suministro_ids)
        acumulados: dict[str, float] = {}
        for (sid, fecha), kwh in self._consumos.items():
            if sid in ids_set and desde <= fecha <= hasta:
                acumulados[sid] = acumulados.get(sid, 0.0) + kwh
        return [(sid, round(total, 2)) for sid, total in acumulados.items()]
