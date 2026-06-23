from __future__ import annotations

import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from domain.ports.consumo_horario_repository import ConsumoHorarioRepository


@dataclass(frozen=True)
class HoraPicoResultado:
    hora_pico: int
    kwh_promedio: float
    perfil_24h: list[tuple[int, float]]  # [(hora, kwh_promedio), ...] len=24


class IdentificarHoraPicoUseCase:
    def __init__(self, repo: ConsumoHorarioRepository) -> None:
        self._repo = repo

    async def ejecutar(self, suministro_id: str, mes: date) -> HoraPicoResultado | None:
        desde = mes.replace(day=1)
        ultimo_dia = calendar.monthrange(mes.year, mes.month)[1]
        hasta = mes.replace(day=ultimo_dia)

        serie = await self._repo.get_serie_horaria_rango(suministro_id, desde, hasta)
        if not serie:
            return None

        totales: dict[int, list[float]] = defaultdict(list)
        for _fecha, hora, kwh in serie:
            totales[hora].append(kwh)

        perfil = {hora: sum(vals) / len(vals) for hora, vals in totales.items()}
        hora_pico = max(perfil, key=lambda h: perfil[h])

        perfil_completo = [(h, round(perfil.get(h, 0.0), 4)) for h in range(24)]

        return HoraPicoResultado(
            hora_pico=hora_pico,
            kwh_promedio=round(perfil[hora_pico], 4),
            perfil_24h=perfil_completo,
        )
