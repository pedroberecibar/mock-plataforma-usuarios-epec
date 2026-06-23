import os
from typing import Any

import httpx

from domain.documento_pago import DocumentoPago
from domain.ports.factura_verificacion_port import FacturaVerificacionPort

# Orden correcto: contrato primero, cliente segundo (confirmado por API real EPEC)
_EPEC_URL = "https://www.epec.com.ar/api/contratos/no-ov/{ct}/{nc}"
_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "es-419,es;q=0.9",
    "apikey": os.environ.get("EPEC_API_KEY", "web-prod"),
    "referrer": "https://www.epec.com.ar/tramites/pagos",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


def _parse_documento(item: dict[str, Any]) -> DocumentoPago:
    # Los nombres exactos de campos son inciertos; se cubren variantes conocidas.
    return DocumentoPago(
        periodo=str(item.get("periodo", "")),
        nro_factura=str(
            item.get("nroComprobante", item.get("nroFactura", item.get("factura", "")))
        ),
        importe=float(item.get("importe", item.get("total", 0))),
        fecha_vencimiento=str(item.get("fechaVencimiento", item.get("vencimiento", ""))),
    )


class EpecFacturaVerificacion(FacturaVerificacionPort):
    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        url = _EPEC_URL.format(ct=numero_contrato, nc=numero_cliente)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=_HEADERS)
            return response.is_success

    async def obtener_documentos(
        self, numero_cliente: str, numero_contrato: str
    ) -> list[DocumentoPago]:
        url = _EPEC_URL.format(ct=numero_contrato, nc=numero_cliente)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=_HEADERS)
        if not response.is_success:
            raise ValueError(
                f"Contrato {numero_contrato} no encontrado para cliente {numero_cliente}"
            )
        if not response.content:
            return []
        items = response.json()
        if isinstance(items, dict):
            items = items.get("documentos", [])
        return [_parse_documento(item) for item in items]
