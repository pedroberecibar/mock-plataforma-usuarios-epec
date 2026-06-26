from datetime import date

import httpx
import pytest

from domain.ports.factura_identificadores import FacturaIdentificadores
from infrastructure.epec.epec_documentos_source_reader import (
    EpecDocumentosSourceReader,
    parse_documento_a_pagar,
    seleccionar_documento,
)
from infrastructure.fakes.factura_identificadores import (
    FakeFacturaIdentificadoresCache,
    FakeFacturaIdentificadoresReader,
)

# ---------------------------------------------------------------------------
# Parsing puro
# ---------------------------------------------------------------------------

_DOC = {
    "id": "F708669297",
    "periodo": "07/2026",
    "importe": "             133,372.90",
    "vencimiento": "30/06/2026",
    "estado": "pagar",
    "urlDocumento": "/api/reportes/abc123",
}


def test_parse_vencimiento_ddmmyyyy_a_date() -> None:
    r = parse_documento_a_pagar(_DOC, base_url="https://www.epec.com.ar")
    assert r.fecha_vencimiento == date(2026, 6, 30)


def test_parse_importe_con_padding_y_separadores() -> None:
    r = parse_documento_a_pagar(_DOC, base_url="https://www.epec.com.ar")
    assert r.importe == 133372.90


def test_parse_url_pdf_absoluta() -> None:
    r = parse_documento_a_pagar(_DOC, base_url="https://www.epec.com.ar")
    assert r.url_pdf == "https://www.epec.com.ar/api/reportes/abc123"


def test_parse_periodo() -> None:
    r = parse_documento_a_pagar(_DOC, base_url="https://www.epec.com.ar")
    assert r.periodo == "07/2026"


def test_seleccionar_documento_toma_el_de_vencimiento_mas_reciente() -> None:
    viejo = {**_DOC, "vencimiento": "08/02/2023"}
    nuevo = {**_DOC, "vencimiento": "30/06/2026"}
    assert seleccionar_documento([viejo, nuevo]) is nuevo


# ---------------------------------------------------------------------------
# Orquestación: cache + oracle + HTTP
# ---------------------------------------------------------------------------


def _transport(payload: object, status: int = 200) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload)

    return httpx.MockTransport(handler)


def _reader_con(
    *,
    cache: FakeFacturaIdentificadoresCache,
    oracle: FakeFacturaIdentificadoresReader,
    payload: object,
    status: int = 200,
) -> EpecDocumentosSourceReader:
    return EpecDocumentosSourceReader(
        cache=cache,
        identificadores_reader=oracle,
        api_key="web-prod",
        transport=_transport(payload, status),
    )


async def test_resuelve_factura_real_con_ids_de_oracle() -> None:
    cache = FakeFacturaIdentificadoresCache()
    oracle = FakeFacturaIdentificadoresReader(
        {"SRV-2817670": FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")}
    )
    payload = {"pagoOnlineHabilitado": "S", "documentosAPagar": [_DOC]}
    reader = _reader_con(cache=cache, oracle=oracle, payload=payload)

    r = await reader.get_factura("SRV-2817670")

    assert r is not None
    assert r.fecha_vencimiento == date(2026, 6, 30)
    assert r.importe == 133372.90
    assert r.pago_online is True


async def test_cachea_los_ids_tras_resolver_en_oracle() -> None:
    cache = FakeFacturaIdentificadoresCache()
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    oracle = FakeFacturaIdentificadoresReader({"SRV-2817670": ids})
    reader = _reader_con(
        cache=cache,
        oracle=oracle,
        payload={"documentosAPagar": [_DOC]},
    )

    await reader.get_factura("SRV-2817670")

    assert await cache.get("SRV-2817670") == ids


async def test_usa_cache_y_no_consulta_oracle_si_ya_esta_cacheado() -> None:
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})  # vacío: fallaría si lo consultara
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": [_DOC]})

    r = await reader.get_factura("SRV-2817670")

    assert r is not None
    assert oracle.llamadas == []


async def test_devuelve_none_si_no_hay_documentos_a_pagar() -> None:
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": []})

    assert await reader.get_factura("SRV-2817670") is None


async def test_devuelve_none_si_suministro_sin_identificadores() -> None:
    cache = FakeFacturaIdentificadoresCache()
    oracle = FakeFacturaIdentificadoresReader({})  # no resuelve
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": [_DOC]})

    assert await reader.get_factura("SRV-9999999") is None


async def test_devuelve_none_si_epec_responde_error() -> None:
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})
    reader = _reader_con(cache=cache, oracle=oracle, payload={"error": "x"}, status=400)

    assert await reader.get_factura("SRV-2817670") is None


@pytest.mark.parametrize("falta", ["vencimiento", "importe"])
async def test_tolera_documento_con_campos_faltantes(falta: str) -> None:
    doc = {k: v for k, v in _DOC.items() if k != falta}
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": [doc]})

    r = await reader.get_factura("SRV-2817670")
    assert r is not None  # no explota; el campo faltante queda en None


# ---------------------------------------------------------------------------
# get_cuenta_factura: lista completa + deuda total
# ---------------------------------------------------------------------------

_DOC_2 = {
    "id": "F999",
    "periodo": "06/2026",
    "importe": "              1,000.10",
    "vencimiento": "08/02/2023",
    "estado": "vencida",
    "urlDocumento": "/api/reportes/xyz",
}


async def test_cuenta_devuelve_todos_los_documentos_y_total() -> None:
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})
    payload = {"pagoOnlineHabilitado": "S", "documentosAPagar": [_DOC, _DOC_2]}
    reader = _reader_con(cache=cache, oracle=oracle, payload=payload)

    cuenta = await reader.get_cuenta_factura("SRV-2817670")

    assert cuenta is not None
    assert len(cuenta.documentos) == 2
    assert cuenta.total_deuda == round(133372.90 + 1000.10, 2)
    assert cuenta.pago_online is True
    assert cuenta.documentos[0].url_pdf == "https://www.epec.com.ar/api/reportes/abc123"


async def test_cuenta_devuelve_none_si_no_hay_documentos() -> None:
    ids = FacturaIdentificadores(cliente_id="1109294", contrato_id="0281767003")
    cache = FakeFacturaIdentificadoresCache({"SRV-2817670": ids})
    oracle = FakeFacturaIdentificadoresReader({})
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": []})

    assert await reader.get_cuenta_factura("SRV-2817670") is None


async def test_cuenta_devuelve_none_si_suministro_sin_identificadores() -> None:
    cache = FakeFacturaIdentificadoresCache()
    oracle = FakeFacturaIdentificadoresReader({})
    reader = _reader_con(cache=cache, oracle=oracle, payload={"documentosAPagar": [_DOC]})

    assert await reader.get_cuenta_factura("SRV-9999999") is None
