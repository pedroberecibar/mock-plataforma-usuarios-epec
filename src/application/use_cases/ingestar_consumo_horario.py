from dataclasses import dataclass
from datetime import date, timedelta

from domain.lecturas_horarias import LecturaHoraria
from domain.ports.consumo_horario_repository import ConsumoHorarioRepository
from domain.ports.medicion_horaria_source_reader import MedicionHorariaSourceReader
from domain.ports.suministro_repository import SuministroRepository


@dataclass(frozen=True)
class IngestaHorariaResultado:
    suministros_procesados: int
    horas_procesadas: int


class IngestarConsumoHorarioUseCase:
    def __init__(
        self,
        reader: MedicionHorariaSourceReader,
        repo: ConsumoHorarioRepository,
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
    ) -> IngestaHorariaResultado:
        lecturas = await self._reader.leer_lecturas_horarias(desde, hasta, equipos=equipos)
        lecturas = self._filtrar_y_deduplicar(lecturas)
        por_equipo = self._agrupar_por_equipo(lecturas)

        horas_total = 0
        for _equipo, serie in por_equipo.items():
            serie_ordenada = sorted(serie, key=lambda lec: (lec.fecha, lec.hora))
            srv_codigo = serie_ordenada[0].srv_codigo
            await self._suministro_repo.crear_placeholder(srv_codigo)
            horas = await self._persistir_serie(srv_codigo, serie_ordenada)
            horas_total += horas

        return IngestaHorariaResultado(
            suministros_procesados=len(por_equipo),
            horas_procesadas=horas_total,
        )

    @staticmethod
    def _filtrar_y_deduplicar(lecturas: list[LecturaHoraria]) -> list[LecturaHoraria]:
        filtradas = [lec for lec in lecturas if lec.cdr_codigo == "E"]
        vistas: dict[tuple[str, date, int], LecturaHoraria] = {}
        for lec in filtradas:
            key = (lec.equipo, lec.fecha, lec.hora)
            if key not in vistas:
                vistas[key] = lec
        return list(vistas.values())

    @staticmethod
    def _agrupar_por_equipo(
        lecturas: list[LecturaHoraria],
    ) -> dict[str, list[LecturaHoraria]]:
        grupos: dict[str, list[LecturaHoraria]] = {}
        for lec in lecturas:
            grupos.setdefault(lec.equipo, []).append(lec)
        return grupos

    async def _persistir_serie(self, srv_codigo: str, serie: list[LecturaHoraria]) -> int:
        """Para cada par consecutivo calcula la tasa horaria uniforme y persiste."""
        horas = 0
        for i in range(len(serie) - 1):
            curr = serie[i]
            nxt = serie[i + 1]

            delta_kwh = nxt.valor_kwh - curr.valor_kwh
            elapsed_hours = (nxt.fecha - curr.fecha).days * 24 + nxt.hora - curr.hora

            if elapsed_hours <= 0 or delta_kwh < 0:
                continue

            rate = round(delta_kwh / elapsed_hours, 4)

            for offset in range(elapsed_hours):
                total_horas = curr.hora + offset
                dia = curr.fecha + timedelta(days=total_horas // 24)
                hora_del_dia = total_horas % 24
                await self._repo.upsert_consumo_horario(srv_codigo, dia, hora_del_dia, rate)
                horas += 1

        return horas
