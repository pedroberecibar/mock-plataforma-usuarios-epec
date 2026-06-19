from domain.ports.factura_verificacion_port import FacturaVerificacionPort


class FakeFacturaVerificacionPort(FacturaVerificacionPort):
    def __init__(self, resultado: bool = True) -> None:
        self._resultado = resultado
        self.llamadas: list[tuple[str, str]] = []

    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        self.llamadas.append((numero_cliente, numero_contrato))
        return self._resultado
