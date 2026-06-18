from urllib.parse import urlencode


class ObtenerLinkFacturaUseCase:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    async def ejecutar(self, numero_cliente: str, numero_contrato: str) -> str:
        params = urlencode({"nc": numero_cliente, "ct": numero_contrato})
        return f"{self._base_url}?{params}"
