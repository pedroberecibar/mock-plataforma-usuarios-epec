from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from application.use_cases.obtener_documentos_factura import ObtenerDocumentosFacturaUseCase
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

    class FacturaDocumentoResponse(BaseModel):
        periodo: str | None = None
        importe: float | None = None
        fecha_vencimiento: date | None = None
        estado: str | None = None
        url_pdf: str | None = None

    class FacturaDatosResponse(BaseModel):
        total_deuda: float = 0.0
        pago_online: bool = False
        cliente_id: str | None = None
        contrato_id: str | None = None
        documentos: list[FacturaDocumentoResponse] = []

    class DocumentoPagoResponse(BaseModel):
        periodo: str
        nro_factura: str
        importe: float
        fecha_vencimiento: str

    @router.get("/datos", response_model=FacturaDatosResponse)
    async def get_factura_datos(
        suministro_id: str = Depends(get_suministro_actual),
        factura_reader: FacturaSourceReader = Depends(get_factura_reader),
    ) -> FacturaDatosResponse:
        cuenta = await factura_reader.get_cuenta_factura(suministro_id)
        if cuenta is None:
            return FacturaDatosResponse()
        return FacturaDatosResponse(
            total_deuda=cuenta.total_deuda,
            pago_online=cuenta.pago_online,
            cliente_id=cuenta.cliente_id,
            contrato_id=cuenta.contrato_id,
            documentos=[
                FacturaDocumentoResponse(
                    periodo=d.periodo,
                    importe=d.importe,
                    fecha_vencimiento=d.fecha_vencimiento,
                    estado=d.estado,
                    url_pdf=d.url_pdf,
                )
                for d in cuenta.documentos
            ],
        )

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

    @router.get("/documentos", response_model=list[DocumentoPagoResponse])
    async def get_documentos_factura(
        numero_cliente: str = Query(..., pattern=r"^\d+$"),
        numero_contrato: str = Query(..., pattern=r"^\d+$"),
        _usuario: str = Depends(get_usuario_actual),
        verificacion_port: FacturaVerificacionPort = Depends(get_factura_verificacion),
    ) -> list[DocumentoPagoResponse]:
        uc = ObtenerDocumentosFacturaUseCase(verificacion_port=verificacion_port)
        try:
            docs = await uc.ejecutar(numero_cliente, numero_contrato)
            return [
                DocumentoPagoResponse(
                    periodo=d.periodo,
                    nro_factura=d.nro_factura,
                    importe=d.importe,
                    fecha_vencimiento=d.fecha_vencimiento,
                )
                for d in docs
            ]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception:
            raise HTTPException(
                status_code=503, detail="Servicio de facturación no disponible"
            ) from None

    return router
