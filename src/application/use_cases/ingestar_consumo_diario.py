from datetime import date, timedelta

from domain.lecturas import LecturaTelemedida
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.medicion_source_reader import MedicionSourceReader


class IngestarConsumoDiarioUseCase:
    def __init__(
        self,
        reader: MedicionSourceReader,
        repo: ConsumoDiarioRepository,
    ) -> None:
        self._reader = reader
        self._repo = repo

    async def ejecutar(self, desde: date, hasta: date) -> None:
        lecturas = await self._reader.leer_lecturas(desde, hasta)
        lecturas = self._filtrar_y_deduplicar(lecturas)
        por_equipo = self._agrupar_por_equipo(lecturas)

        for equipo, serie in por_equipo.items():
            serie_ordenada = sorted(serie, key=lambda lect: lect.fecha)
            await self._persistir_serie(equipo, serie_ordenada)

    # ------------------------------------------------------------------
    # helpers privados
    # ------------------------------------------------------------------

    @staticmethod
    def _filtrar_y_deduplicar(lecturas: list[LecturaTelemedida]) -> list[LecturaTelemedida]:
        filtradas = [lect for lect in lecturas if lect.cdr_codigo == "E"]
        # dedupe: mantiene un registro por (equipo, fecha); en caso de duplicado,
        # el primero encontrado gana (los valores son idénticos por definición del seed)
        vistas: dict[tuple[str, date], LecturaTelemedida] = {}
        for lect in filtradas:
            key = (lect.equipo, lect.fecha)
            if key not in vistas:
                vistas[key] = lect
        return list(vistas.values())

    @staticmethod
    def _agrupar_por_equipo(
        lecturas: list[LecturaTelemedida],
    ) -> dict[str, list[LecturaTelemedida]]:
        grupos: dict[str, list[LecturaTelemedida]] = {}
        for lect in lecturas:
            grupos.setdefault(lect.equipo, []).append(lect)
        return grupos

    async def _persistir_serie(self, equipo: str, serie: list[LecturaTelemedida]) -> None:
        """Para cada par consecutivo de lecturas acumulativas calcula la tasa
        diaria uniforme y persiste un registro por cada día del intervalo
        [fecha_curr, fecha_next)."""
        for i in range(len(serie) - 1):
            curr = serie[i]
            nxt = serie[i + 1]

            delta_kwh = nxt.valor_kwh - curr.valor_kwh
            delta_days = (nxt.fecha - curr.fecha).days

            if delta_days <= 0 or delta_kwh < 0:
                continue

            rate = round(delta_kwh / delta_days, 2)

            for offset in range(delta_days):
                dia = curr.fecha + timedelta(days=offset)
                await self._repo.upsert_consumo(equipo, dia, rate)
