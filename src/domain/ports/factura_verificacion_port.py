import abc


class FacturaVerificacionPort(abc.ABC):
    @abc.abstractmethod
    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        """Verifica que el contrato existe en el sistema de EPEC. Devuelve True si válido."""
