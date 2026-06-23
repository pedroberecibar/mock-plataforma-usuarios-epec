from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_horario_repository import ConsumoHorarioRepository


@dataclass(frozen=True)
class SerieHorariaResultado:
    fecha: date
    puntos: list[tuple[int, float]]  # [(hora, kWh), ...]


class ObtenerSerieHorariaUseCase:
    def __init__(self, repo: ConsumoHorarioRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str, fecha: date) -> SerieHorariaResultado:
        puntos = await self._repo.get_serie_horaria(suministro_id, fecha)
        return SerieHorariaResultado(fecha=fecha, puntos=puntos)
