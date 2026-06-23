import abc

from domain.documento_pago import DocumentoPago


class FacturaVerificacionPort(abc.ABC):
    @abc.abstractmethod
    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        """Verifica que el contrato existe en el sistema de EPEC. Devuelve True si válido."""

    @abc.abstractmethod
    async def obtener_documentos(
        self, numero_cliente: str, numero_contrato: str
    ) -> list[DocumentoPago]:
        """Retorna los documentos de pago pendientes del contrato.
        Lista vacía = contrato válido sin facturas pendientes.
        Lanza ValueError si el contrato no existe."""
