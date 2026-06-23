from domain.documento_pago import DocumentoPago
from domain.ports.factura_verificacion_port import FacturaVerificacionPort


class FakeFacturaVerificacionPort(FacturaVerificacionPort):
    def __init__(
        self,
        resultado: bool = True,
        documentos: list[DocumentoPago] | None = None,
        contrato_invalido: bool = False,
    ) -> None:
        self._resultado = resultado
        self._documentos = documentos if documentos is not None else []
        self._contrato_invalido = contrato_invalido
        self.llamadas: list[tuple[str, str]] = []
        self.llamadas_documentos: list[tuple[str, str]] = []

    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        self.llamadas.append((numero_cliente, numero_contrato))
        return self._resultado

    async def obtener_documentos(
        self, numero_cliente: str, numero_contrato: str
    ) -> list[DocumentoPago]:
        self.llamadas_documentos.append((numero_cliente, numero_contrato))
        if self._contrato_invalido:
            raise ValueError(
                f"Contrato {numero_contrato} no encontrado para cliente {numero_cliente}"
            )
        return self._documentos
