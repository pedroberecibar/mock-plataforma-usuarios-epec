import httpx

from domain.ports.factura_verificacion_port import FacturaVerificacionPort

_EPEC_URL = "https://www.epec.com.ar/api/contratos/no-ov/{nc}/{ct}"
_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "es-419,es;q=0.9",
    "apikey": "web-prod",
    "headername": "headerValue",
    "referrer": "https://www.epec.com.ar/tramites/pagos",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


class EpecFacturaVerificacion(FacturaVerificacionPort):
    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        url = _EPEC_URL.format(nc=numero_cliente, ct=numero_contrato)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=_HEADERS)
            return response.is_success
