from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase
from domain.ports.factura_source_reader import FacturaSourceReader
from interface.dependencies import get_factura_reader, get_suministro_actual, get_usuario_actual


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
        numero_cliente: str,
        numero_contrato: str,
        _usuario: str = Depends(get_usuario_actual),
    ) -> LinkResponse:
        if epec_base_url is None:
            raise HTTPException(
                status_code=503,
                detail="Redirección a EPEC no configurada — definir EPEC_FACTURA_BASE_URL",
            )
        uc = ObtenerLinkFacturaUseCase(base_url=epec_base_url)
        url = await uc.ejecutar(numero_cliente, numero_contrato)
        return LinkResponse(url=url)

    return router
