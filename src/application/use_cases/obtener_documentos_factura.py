from domain.documento_pago import DocumentoPago
from domain.ports.factura_verificacion_port import FacturaVerificacionPort


class ObtenerDocumentosFacturaUseCase:
    def __init__(self, verificacion_port: FacturaVerificacionPort) -> None:
        self._port = verificacion_port

    async def ejecutar(self, numero_cliente: str, numero_contrato: str) -> list[DocumentoPago]:
        return await self._port.obtener_documentos(numero_cliente, numero_contrato)
