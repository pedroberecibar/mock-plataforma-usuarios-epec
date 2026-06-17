from dataclasses import dataclass
from datetime import date, timedelta

from domain.lecturas import LecturaTelemedida
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.suministro_repository import SuministroRepository


@dataclass(frozen=True)
class IngestaResultado:
    suministros_procesados: int
    dias_procesados: int


class IngestarConsumoDiarioUseCase:
    def __init__(
        self,
        reader: MedicionSourceReader,
        repo: ConsumoDiarioRepository,
        suministro_repo: SuministroRepository,
    ) -> None:
        self._reader = reader
        self._repo = repo
        self._suministro_repo = suministro_repo

    async def ejecutar(
        self,
        desde: date,
        hasta: date,
        equipos: list[str] | None = None,
    ) -> IngestaResultado:
        lecturas = await self._reader.leer_lecturas(desde, hasta, equipos=equipos)
        lecturas = self._filtrar_y_deduplicar(lecturas)
        por_equipo = self._agrupar_por_equipo(lecturas)

        dias_total = 0
        for _equipo, serie in por_equipo.items():
            serie_ordenada = sorted(serie, key=lambda lect: lect.fecha)
            srv_codigo = serie_ordenada[0].srv_codigo
            await self._suministro_repo.crear_placeholder(srv_codigo)
            dias = await self._persistir_serie(srv_codigo, serie_ordenada)
            dias_total += dias

        return IngestaResultado(
            suministros_procesados=len(por_equipo),
            dias_procesados=dias_total,
        )

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

    async def _persistir_serie(self, srv_codigo: str, serie: list[LecturaTelemedida]) -> int:
        """Para cada par consecutivo de lecturas acumulativas calcula la tasa
        diaria uniforme y persiste un registro por cada día del intervalo
        [fecha_curr, fecha_next). Retorna la cantidad de días persistidos."""
        dias = 0
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
                await self._repo.upsert_consumo(srv_codigo, dia, rate)
                dias += 1

        return dias
