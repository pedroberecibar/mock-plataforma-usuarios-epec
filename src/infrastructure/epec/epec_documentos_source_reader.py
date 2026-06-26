"""Adapter que trae la factura real de EPEC vía POST /api/documentos/a-pagar.

Resuelve cliente/contrato del suministro (cache SQLite → Oracle), llama a la API
pública de EPEC y mapea el documento a `FacturaResult`. Ver
`docs/epec-factura-api-referencia.md`.
"""

from __future__ import annotations

import datetime as dt
import os
from typing import Any

import httpx

from domain.ports.factura_identificadores import (
    FacturaIdentificadores,
    FacturaIdentificadoresCache,
    FacturaIdentificadoresReader,
)
from domain.ports.factura_source_reader import (
    FacturaCuenta,
    FacturaDocumento,
    FacturaResult,
    FacturaSourceReader,
)

_BASE_URL = "https://www.epec.com.ar"
_DOCUMENTOS_PATH = "/api/documentos/a-pagar"
_DEFAULT_API_KEY = "web-prod"
_TIMEOUT = 20.0


def _parse_fecha(value: object) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.strptime(str(value).strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def _parse_importe(value: object) -> float | None:
    if value is None:
        return None
    texto = str(value).strip().replace(",", "")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def _periodo(item: dict[str, Any]) -> str | None:
    return str(item["periodo"]).strip() if item.get("periodo") else None


def _url_pdf(item: dict[str, Any], base_url: str) -> str | None:
    url_doc = item.get("urlDocumento")
    return f"{base_url}{url_doc}" if url_doc else None


def parse_documento_a_pagar(item: dict[str, Any], base_url: str) -> FacturaResult:
    """Mapea un elemento de `documentosAPagar` a `FacturaResult` (campos faltantes → None)."""
    return FacturaResult(
        fecha_vencimiento=_parse_fecha(item.get("vencimiento")),
        importe=_parse_importe(item.get("importe")),
        periodo=_periodo(item),
        url_pdf=_url_pdf(item, base_url),
    )


def parse_documento(item: dict[str, Any], base_url: str) -> FacturaDocumento:
    """Mapea un elemento de `documentosAPagar` a `FacturaDocumento`."""
    return FacturaDocumento(
        periodo=_periodo(item),
        importe=_parse_importe(item.get("importe")),
        fecha_vencimiento=_parse_fecha(item.get("vencimiento")),
        estado=(str(item["estado"]).strip() if item.get("estado") else None),
        url_pdf=_url_pdf(item, base_url),
    )


def seleccionar_documento(documentos: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Elige el documento con el vencimiento más reciente (la factura vigente)."""
    if not documentos:
        return None
    return max(documentos, key=lambda d: _parse_fecha(d.get("vencimiento")) or dt.date.min)


class EpecDocumentosSourceReader(FacturaSourceReader):
    def __init__(
        self,
        cache: FacturaIdentificadoresCache,
        identificadores_reader: FacturaIdentificadoresReader,
        api_key: str | None = None,
        base_url: str = _BASE_URL,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._cache = cache
        self._reader = identificadores_reader
        self._api_key = api_key or os.environ.get("EPEC_API_KEY", _DEFAULT_API_KEY)
        self._base_url = base_url
        self._transport = transport

    async def _resolver_ids(self, suministro_id: str) -> FacturaIdentificadores | None:
        cached = await self._cache.get(suministro_id)
        if cached is not None:
            return cached
        ids = await self._reader.leer(suministro_id)
        if ids is not None:
            await self._cache.guardar(suministro_id, ids)
        return ids

    async def _fetch(self, ids: FacturaIdentificadores) -> tuple[list[dict[str, Any]], bool]:
        """Devuelve (documentosAPagar, pago_online_habilitado)."""
        headers = {
            "content-type": "application/json",
            "apiKey": self._api_key,
            "Origin": self._base_url,
            "Referer": f"{self._base_url}/tramites/pagos",
        }
        body = {"contratoId": ids.contrato_id, "clienteId": ids.cliente_id}
        async with httpx.AsyncClient(timeout=_TIMEOUT, transport=self._transport) as client:
            resp = await client.post(
                f"{self._base_url}{_DOCUMENTOS_PATH}", headers=headers, json=body
            )
        if not resp.is_success or not resp.content:
            return [], False
        data = resp.json()
        if not isinstance(data, dict):
            return [], False
        documentos = list(data.get("documentosAPagar") or [])
        pago_online = str(data.get("pagoOnlineHabilitado", "")).upper() == "S"
        return documentos, pago_online

    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        ids = await self._resolver_ids(suministro_id)
        if ids is None:
            return None
        try:
            documentos, pago_online = await self._fetch(ids)
        except httpx.HTTPError:
            return None
        elegido = seleccionar_documento(documentos)
        if elegido is None:
            return None
        result = parse_documento_a_pagar(elegido, self._base_url)
        result.pago_online = pago_online
        return result

    async def get_cuenta_factura(self, suministro_id: str) -> FacturaCuenta | None:
        ids = await self._resolver_ids(suministro_id)
        if ids is None:
            return None
        try:
            documentos, pago_online = await self._fetch(ids)
        except httpx.HTTPError:
            return None
        if not documentos:
            return None
        docs = [parse_documento(d, self._base_url) for d in documentos]
        total = round(sum(d.importe or 0.0 for d in docs), 2)
        return FacturaCuenta(documentos=docs, total_deuda=total, pago_online=pago_online)
