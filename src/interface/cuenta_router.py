from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.use_cases.obtener_cuenta import CuentaResult, ObtenerCuentaUseCase
from domain.ports.cuenta_reader import CuentaReader
from domain.ports.cuenta_sensible_repository import CuentaSensibleRepository
from domain.ports.pii_cipher import PiiCipher
from domain.ports.usuario_repository import UsuarioRepository
from interface.dependencies import (
    get_cuenta_reader,
    get_cuenta_sensible_repo,
    get_pii_cipher,
    get_suministro_actual,
    get_usuario_actual,
    get_usuario_repo,
)

router = APIRouter(prefix="/cuenta", tags=["cuenta"])


class PersonalesResponse(BaseModel):
    nombre_o_razon_social: str | None
    tipo_documento: str | None
    nro_documento_masked: str | None
    cuit_masked: str | None
    email: str | None


class SuministroResponse(BaseModel):
    numero: str
    estado_servicio: str | None
    direccion: str | None
    barrio: str | None
    localidad: str | None
    cp: str | None


class TarifaResponse(BaseModel):
    codigo: str | None
    descripcion: str | None
    grupo_tarifario: str | None
    clase: str | None
    clase_descripcion: str | None
    tension: str | None


class MedidorResponse(BaseModel):
    numero: str | None
    marca: str | None
    fase: str
    inteligente_desde: str | None


class CuentaResponse(BaseModel):
    personales: PersonalesResponse
    suministro: SuministroResponse
    tarifa: TarifaResponse
    medidor: MedidorResponse


def _to_response(result: CuentaResult) -> CuentaResponse:
    return CuentaResponse(
        personales=PersonalesResponse(**vars(result.personales)),
        suministro=SuministroResponse(**vars(result.suministro)),
        tarifa=TarifaResponse(**vars(result.tarifa)),
        medidor=MedidorResponse(
            numero=result.medidor.numero,
            marca=result.medidor.marca,
            fase=result.medidor.fase,
            inteligente_desde=(
                result.medidor.inteligente_desde.isoformat()
                if result.medidor.inteligente_desde is not None
                else None
            ),
        ),
    )


@router.get("", response_model=CuentaResponse)
async def get_cuenta(
    usuario: str = Depends(get_usuario_actual),
    suministro_id: str = Depends(get_suministro_actual),
    cuenta_reader: CuentaReader = Depends(get_cuenta_reader),
    usuario_repo: UsuarioRepository = Depends(get_usuario_repo),
    pii_cipher: PiiCipher = Depends(get_pii_cipher),
    sensible_repo: CuentaSensibleRepository = Depends(get_cuenta_sensible_repo),
) -> CuentaResponse:
    uc = ObtenerCuentaUseCase(
        cuenta_reader=cuenta_reader,
        usuario_repo=usuario_repo,
        pii_cipher=pii_cipher,
        sensible_repo=sensible_repo,
    )
    result = await uc.ejecutar(usuario, suministro_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No se encontraron datos del suministro")
    return _to_response(result)
