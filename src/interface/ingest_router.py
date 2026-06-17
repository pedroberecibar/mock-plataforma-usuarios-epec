from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.suministro_repository import SuministroRepository
from interface.dependencies import (
    get_consumo_repo,
    get_medicion_reader,
    get_suministro_repo,
    get_usuario_actual,
)

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestaResponse(BaseModel):
    ok: bool
    suministros_procesados: int
    dias_procesados: int


@router.post("/consumo", response_model=IngestaResponse)
async def ingestar_consumo(
    desde: date,
    hasta: date,
    _usuario: str = Depends(get_usuario_actual),
    reader: MedicionSourceReader = Depends(get_medicion_reader),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
    suministro_repo: SuministroRepository = Depends(get_suministro_repo),
) -> IngestaResponse:
    # El reader inyectado ya está envuelto en _NonBlockingReader por main.py (composition root).
    # Itera de a 1 día: ~380K filas/día es manejable en memoria; el rango completo no lo es.
    suministros_total = 0
    dias_total = 0
    dia = desde
    while dia <= hasta:
        resultado = await IngestarConsumoDiarioUseCase(
            reader, consumo_repo, suministro_repo
        ).ejecutar(dia, dia)
        suministros_total = max(suministros_total, resultado.suministros_procesados)
        dias_total += resultado.dias_procesados
        dia += timedelta(days=1)
    return IngestaResponse(
        ok=True,
        suministros_procesados=suministros_total,
        dias_procesados=dias_total,
    )
