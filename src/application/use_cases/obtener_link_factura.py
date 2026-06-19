from domain.ports.factura_verificacion_port import FacturaVerificacionPort


class ObtenerLinkFacturaUseCase:
    def __init__(
        self,
        verificacion_port: FacturaVerificacionPort,
        base_url: str | None = None,
    ) -> None:
        self._verificacion_port = verificacion_port
        self._base_url = base_url

    async def ejecutar(self, numero_cliente: str, numero_contrato: str) -> str:
        valido = await self._verificacion_port.verificar_contrato(numero_cliente, numero_contrato)
        if not valido:
            raise ValueError(
                f"Contrato {numero_contrato} no encontrado para cliente {numero_cliente}"
            )
        return self._base_url or "https://www.epec.com.ar/tramites/pagos"
