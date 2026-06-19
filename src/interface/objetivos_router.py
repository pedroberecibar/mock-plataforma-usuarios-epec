from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator

from application.use_cases.calcular_estado_objetivo import (
    CalcularEstadoObjetivoUseCase,
    EstadoObjetivoResult,
    TextoDinamico,
)
from application.use_cases.calcular_objetivo_sugerido import CalcularObjetivoSugeridoUseCase
from application.use_cases.get_objetivo_consumo import GetObjetivoConsumoUseCase, ObjetivoResult
from application.use_cases.set_objetivo_consumo import SetObjetivoConsumoUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from domain.ports.vecinos_repository import VecinosRepository
from interface.dependencies import (
    get_consumo_repo,
    get_objetivo_repo,
    get_suministro_actual,
    get_vecinos_repo,
)

router = APIRouter(prefix="/objetivos", tags=["objetivos"])


class ObjetivoRequest(BaseModel):
    valor_kwh: float

    @field_validator("valor_kwh")
    @classmethod
    def debe_ser_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("valor_kwh debe ser positivo")
        return v


class ObjetivoResponse(BaseModel):
    valor_kwh: float
    origen: str
    vigente_desde: str


def _to_response(resultado: ObjetivoResult) -> ObjetivoResponse:
    return ObjetivoResponse(
        valor_kwh=resultado["valor_kwh"],
        origen=resultado["origen"],
        vigente_desde=str(resultado["vigente_desde"]),
    )


@router.get("", response_model=ObjetivoResponse | None)
async def get_objetivo(
    suministro_id: str = Depends(get_suministro_actual),
    repo: ObjetivoConsumoRepository = Depends(get_objetivo_repo),
) -> ObjetivoResponse | None:
    uc = GetObjetivoConsumoUseCase(repo)
    resultado = await uc.ejecutar(suministro_id)
    if resultado is None:
        return None
    return _to_response(resultado)


@router.post("", response_model=ObjetivoResponse, status_code=201)
async def set_objetivo(
    body: ObjetivoRequest,
    suministro_id: str = Depends(get_suministro_actual),
    repo: ObjetivoConsumoRepository = Depends(get_objetivo_repo),
) -> ObjetivoResponse:
    uc = SetObjetivoConsumoUseCase(repo)
    try:
        await uc.ejecutar(suministro_id, body.valor_kwh)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    get_uc = GetObjetivoConsumoUseCase(repo)
    resultado = await get_uc.ejecutar(suministro_id)
    if resultado is None:
        raise HTTPException(status_code=500, detail="Error interno al guardar objetivo")
    return _to_response(resultado)


class ObjetivoSugeridoResponse(BaseModel):
    valor_kwh: float | None
    n_vecinos: int
    sin_datos: bool


class EstadoObjetivoResponse(BaseModel):
    objetivo_kwh: float | None
    promedio_vecinos_kwh: float | None
    n_vecinos: int
    diferencia_pct: float | None
    dias_transcurridos: int
    dias_objetivo_consumidos: float | None
    texto_dinamico: TextoDinamico
    excedente_kwh: float | None
    consumo_diario_real_kwh: float | None
    consumo_diario_objetivo_kwh: float | None
    consumo_acumulado_kwh: float | None
    consumo_promedio_diario_kwh: float | None


def _parse_mes(mes_str: str) -> date:
    try:
        parts = mes_str.split("-")
        return date(int(parts[0]), int(parts[1]), 1)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="mes debe tener formato YYYY-MM") from exc


@router.get("/sugerido", response_model=ObjetivoSugeridoResponse)
async def get_objetivo_sugerido(
    suministro_id: str = Depends(get_suministro_actual),
    mes: str = Query(default=None, description="YYYY-MM; si se omite se usa el mes actual"),
    vecinos_repo: VecinosRepository = Depends(get_vecinos_repo),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
) -> ObjetivoSugeridoResponse:
    if mes is None:
        hoy = date.today()
        mes_date = date(hoy.year, hoy.month, 1)
    else:
        mes_date = _parse_mes(mes)

    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar(suministro_id, mes_date)
    return ObjetivoSugeridoResponse(
        valor_kwh=result.valor_kwh,
        n_vecinos=result.n_vecinos,
        sin_datos=result.sin_datos,
    )


@router.get("/estado", response_model=EstadoObjetivoResponse)
async def get_estado_objetivo(
    suministro_id: str = Depends(get_suministro_actual),
    mes: str = Query(default=None, description="YYYY-MM; si se omite se usa el mes actual"),
    hoy: str = Query(default=None, description="YYYY-MM-DD; solo para tests"),
    objetivo_repo: ObjetivoConsumoRepository = Depends(get_objetivo_repo),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
    vecinos_repo: VecinosRepository = Depends(get_vecinos_repo),
) -> EstadoObjetivoResponse:
    hoy_date: date | None = None
    if hoy is not None:
        try:
            hoy_date = date.fromisoformat(hoy)
        except ValueError as exc:
            raise HTTPException(
                status_code=422, detail="hoy debe tener formato YYYY-MM-DD"
            ) from exc

    if mes is None:
        hoy_real = hoy_date or date.today()
        mes_date = date(hoy_real.year, hoy_real.month, 1)
    else:
        mes_date = _parse_mes(mes)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result: EstadoObjetivoResult = await uc.ejecutar(suministro_id, mes_date, hoy=hoy_date)
    return EstadoObjetivoResponse(
        objetivo_kwh=result.objetivo_kwh,
        promedio_vecinos_kwh=result.promedio_vecinos_kwh,
        n_vecinos=result.n_vecinos,
        diferencia_pct=result.diferencia_pct,
        dias_transcurridos=result.dias_transcurridos,
        dias_objetivo_consumidos=result.dias_objetivo_consumidos,
        texto_dinamico=result.texto_dinamico,
        excedente_kwh=result.excedente_kwh,
        consumo_diario_real_kwh=result.consumo_diario_real_kwh,
        consumo_diario_objetivo_kwh=result.consumo_diario_objetivo_kwh,
        consumo_acumulado_kwh=result.consumo_acumulado_kwh,
        consumo_promedio_diario_kwh=result.consumo_promedio_diario_kwh,
    )
