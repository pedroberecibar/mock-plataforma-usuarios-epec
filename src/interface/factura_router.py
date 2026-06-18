from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase
from interface.dependencies import get_usuario_actual


def build_router(epec_base_url: str | None) -> APIRouter:
    router = APIRouter(prefix="/factura", tags=["factura"])

    class LinkResponse(BaseModel):
        url: str

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
