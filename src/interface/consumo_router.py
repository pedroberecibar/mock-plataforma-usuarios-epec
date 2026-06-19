from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from application.use_cases.detectar_anomalia_consumo import DetectarAnomaliaConsumoUseCase
from application.use_cases.get_detalle_dia import GetDetalleDiaUseCase
from application.use_cases.obtener_comparacion_historica import (
    ObtenerComparacionHistoricaUseCase,
    PeriodoConsumo,
)
from application.use_cases.obtener_serie_diaria import ObtenerSerieDiariaUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.vecinos_repository import VecinosRepository
from interface.dependencies import (
    get_consumo_repo,
    get_suministro_actual,
    get_vecinos_repo,
)

router = APIRouter(prefix="/consumo", tags=["consumo"])


class PuntoSerie(BaseModel):
    fecha: date
    kwh: float


class DiarioResponse(BaseModel):
    serie: list[PuntoSerie]
    datos_hasta: date | None


class PeriodoResponse(BaseModel):
    mes: date
    serie: list[PuntoSerie]
    total_kwh: float | None


class ComparacionResponse(BaseModel):
    mes_actual: PeriodoResponse
    mes_anterior: PeriodoResponse
    mismo_mes_anio_anterior: PeriodoResponse
    datos_hasta: date | None


class DetalleDiaResponse(BaseModel):
    fecha: date
    kwh_dia: float | None
    kwh_mismo_dia_anio_ant: float | None
    kwh_promedio_zona: float | None
    n_vecinos: int


class AnomaliaResponse(BaseModel):
    fecha: date
    kwh: float
    z_score: float
    desviacion_pct: float


@router.get("/dia", response_model=DetalleDiaResponse)
async def get_detalle_dia(
    fecha: date,
    suministro_id: str = Depends(get_suministro_actual),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
    vecinos_repo: VecinosRepository = Depends(get_vecinos_repo),
) -> DetalleDiaResponse:
    result = await GetDetalleDiaUseCase(consumo_repo, vecinos_repo).ejecutar(suministro_id, fecha)
    return DetalleDiaResponse(
        fecha=result.fecha,
        kwh_dia=result.kwh_dia,
        kwh_mismo_dia_anio_ant=result.kwh_mismo_dia_anio_ant,
        kwh_promedio_zona=result.kwh_promedio_zona,
        n_vecinos=result.n_vecinos,
    )


@router.get("/diario", response_model=DiarioResponse)
async def get_consumo_diario(
    desde: date,
    hasta: date,
    suministro_id: str = Depends(get_suministro_actual),
    repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
) -> DiarioResponse:
    resultado = await ObtenerSerieDiariaUseCase(repo).ejecutar(suministro_id, desde, hasta)
    return DiarioResponse(
        serie=[PuntoSerie(fecha=f, kwh=kwh) for f, kwh in resultado.serie],
        datos_hasta=resultado.datos_hasta,
    )


@router.get("/comparacion", response_model=ComparacionResponse)
async def get_comparacion_historica(
    mes: str,
    suministro_id: str = Depends(get_suministro_actual),
    repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
) -> ComparacionResponse:
    try:
        mes_date = datetime.strptime(mes, "%Y-%m").date()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="mes debe tener formato YYYY-MM") from exc

    resultado = await ObtenerComparacionHistoricaUseCase(repo).ejecutar(suministro_id, mes_date)

    def _to_periodo(periodo: PeriodoConsumo) -> PeriodoResponse:
        return PeriodoResponse(
            mes=periodo.mes,
            serie=[PuntoSerie(fecha=f, kwh=kwh) for f, kwh in periodo.serie],
            total_kwh=periodo.total_kwh,
        )

    return ComparacionResponse(
        mes_actual=_to_periodo(resultado.mes_actual),
        mes_anterior=_to_periodo(resultado.mes_anterior),
        mismo_mes_anio_anterior=_to_periodo(resultado.mismo_mes_anio_anterior),
        datos_hasta=resultado.datos_hasta,
    )


@router.get("/anomalia", response_model=AnomaliaResponse | None)
async def get_anomalia_consumo(
    mes: str,
    suministro_id: str = Depends(get_suministro_actual),
    repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
) -> AnomaliaResponse | None:
    try:
        mes_date = datetime.strptime(mes, "%Y-%m").date()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="mes debe tener formato YYYY-MM") from exc

    resultado = await DetectarAnomaliaConsumoUseCase(repo).ejecutar(suministro_id, mes_date)
    if resultado is None:
        return None
    return AnomaliaResponse(
        fecha=resultado.fecha,
        kwh=resultado.kwh,
        z_score=resultado.z_score,
        desviacion_pct=resultado.desviacion_pct,
    )


@router.get("/export/csv")
async def export_consumo_csv(
    desde: date,
    hasta: date,
    suministro_id: str = Depends(get_suministro_actual),
    repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
) -> Response:
    serie = await repo.get_serie(suministro_id, desde, hasta)
    rows = ["fecha,kwh"] + [f"{f},{kwh}" for f, kwh in serie]
    content = "\n".join(rows)
    filename = f"consumo_{suministro_id}_{desde}_{hasta}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
