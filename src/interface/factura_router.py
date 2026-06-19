from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase
from domain.ports.factura_source_reader import FacturaSourceReader
from domain.ports.factura_verificacion_port import FacturaVerificacionPort
from interface.dependencies import (
    get_factura_reader,
    get_factura_verificacion,
    get_suministro_actual,
    get_usuario_actual,
)


def build_router(epec_base_url: str | None) -> APIRouter:
    router = APIRouter(prefix="/factura", tags=["factura"])

    class LinkResponse(BaseModel):
        url: str

    class FacturaDatosResponse(BaseModel):
        fecha_vencimiento: date | None

    @router.get("/datos", response_model=FacturaDatosResponse)
    async def get_factura_datos(
        suministro_id: str = Depends(get_suministro_actual),
        factura_reader: FacturaSourceReader = Depends(get_factura_reader),
    ) -> FacturaDatosResponse:
        factura = await factura_reader.get_factura(suministro_id)
        fecha_vcto = factura.fecha_vencimiento if factura else None
        return FacturaDatosResponse(fecha_vencimiento=fecha_vcto)

    @router.get("/link", response_model=LinkResponse)
    async def get_link_factura(
        numero_cliente: str = Query(..., pattern=r"^\d+$"),
        numero_contrato: str = Query(..., pattern=r"^\d+$"),
        _usuario: str = Depends(get_usuario_actual),
        verificacion_port: FacturaVerificacionPort = Depends(get_factura_verificacion),
    ) -> LinkResponse:
        uc = ObtenerLinkFacturaUseCase(
            verificacion_port=verificacion_port,
            base_url=epec_base_url,
        )
        try:
            url = await uc.ejecutar(numero_cliente, numero_contrato)
            return LinkResponse(url=url)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception:
            raise HTTPException(
                status_code=503, detail="Servicio de facturación no disponible"
            ) from None

    return router
