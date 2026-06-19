import httpx


class ObtenerLinkFacturaUseCase:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url

    async def ejecutar(self, numero_cliente: str, numero_contrato: str) -> str:
        url = f"https://www.epec.com.ar/api/contratos/no-ov/{numero_cliente}/{numero_contrato}"

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "es-419,es;q=0.9",
            "apikey": "web-prod",
            "headername": "headerValue",
            "referrer": "https://www.epec.com.ar/tramites/pagos",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        return self._base_url or "https://www.epec.com.ar/tramites/pagos"
