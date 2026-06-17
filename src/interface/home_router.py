from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.use_cases.calcular_proyeccion_mensual import CalcularProyeccionMensualUseCase
from application.use_cases.obtener_home import ObtenerHomeUseCase
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.ports.vecinos_repository import VecinosRepository
from interface.dependencies import (
    get_consumo_repo,
    get_proyeccion_repo,
    get_usuario_actual,
    get_vecinos_repo,
)

router = APIRouter(prefix="/home", tags=["home"])


class ProyeccionResponse(BaseModel):
    mes: date
    metodo_aplicado: str
    bandera_confianza: str
    rango_inferior_kwh: float | None
    rango_superior_kwh: float | None


class ConsumoMesResponse(BaseModel):
    total_kwh: float | None
    vs_mes_anterior_pct: float | None
    vs_anio_anterior_pct: float | None


class ComparacionZonaResponse(BaseModel):
    promedio_vecinos_kwh: float | None
    n_vecinos: int
    diferencia_pct: float | None


class HomeResponse(BaseModel):
    consumo_mes: ConsumoMesResponse
    comparacion_zona: ComparacionZonaResponse
    proyeccion: ProyeccionResponse
    datos_hasta: date | None
    timestamp: datetime


@router.get("/{suministro_id}", response_model=HomeResponse)
async def get_home(
    suministro_id: str,
    mes: str | None = None,
    _usuario: str = Depends(get_usuario_actual),
    consumo_repo: ConsumoDiarioRepository = Depends(get_consumo_repo),
    vecinos_repo: VecinosRepository = Depends(get_vecinos_repo),
    proyeccion_repo: ProyeccionRepository = Depends(get_proyeccion_repo),
) -> HomeResponse:
    if mes is None:
        mes_date = date.today().replace(day=1)
    else:
        try:
            mes_date = datetime.strptime(mes, "%Y-%m").date()
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="mes debe tener formato YYYY-MM") from exc

    calcular_uc = CalcularProyeccionMensualUseCase(consumo_repo, proyeccion_repo)
    resultado = await ObtenerHomeUseCase(
        consumo_repo, vecinos_repo, proyeccion_repo, calcular_uc
    ).ejecutar(suministro_id, mes_date)

    return HomeResponse(
        consumo_mes=ConsumoMesResponse(
            total_kwh=resultado.consumo_mes.total_kwh,
            vs_mes_anterior_pct=resultado.consumo_mes.vs_mes_anterior_pct,
            vs_anio_anterior_pct=resultado.consumo_mes.vs_anio_anterior_pct,
        ),
        comparacion_zona=ComparacionZonaResponse(
            promedio_vecinos_kwh=resultado.comparacion_zona.promedio_vecinos_kwh,
            n_vecinos=resultado.comparacion_zona.n_vecinos,
            diferencia_pct=resultado.comparacion_zona.diferencia_pct,
        ),
        proyeccion=ProyeccionResponse(
            mes=resultado.proyeccion.mes,
            metodo_aplicado=resultado.proyeccion.metodo_aplicado,
            bandera_confianza=resultado.proyeccion.bandera_confianza,
            rango_inferior_kwh=resultado.proyeccion.rango_inferior_kwh,
            rango_superior_kwh=resultado.proyeccion.rango_superior_kwh,
        ),
        datos_hasta=resultado.datos_hasta,
        timestamp=resultado.timestamp,
    )
