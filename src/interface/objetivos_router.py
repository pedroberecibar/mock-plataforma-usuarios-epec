from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from application.use_cases.get_objetivo_consumo import GetObjetivoConsumoUseCase, ObjetivoResult
from application.use_cases.set_objetivo_consumo import SetObjetivoConsumoUseCase
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository
from interface.dependencies import get_objetivo_repo, get_suministro_actual

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
    assert resultado is not None
    return _to_response(resultado)
