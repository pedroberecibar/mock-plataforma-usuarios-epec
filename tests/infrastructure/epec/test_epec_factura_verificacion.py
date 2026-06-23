from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.documento_pago import DocumentoPago
from infrastructure.epec.epec_factura_verificacion import EpecFacturaVerificacion

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(status: int = 200, body: bytes = b"", json_data: object = None) -> AsyncMock:
    mock_response = MagicMock()
    mock_response.is_success = 200 <= status < 300
    if json_data is not None:
        import json

        raw = json.dumps(json_data).encode()
        mock_response.content = raw
        mock_response.json = MagicMock(return_value=json_data)
    else:
        mock_response.content = body
        mock_response.json = MagicMock(return_value=None)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    return mock_client


# ---------------------------------------------------------------------------
# verificar_contrato
# ---------------------------------------------------------------------------


async def test_url_usa_orden_contrato_cliente() -> None:
    """La API de EPEC espera /no-ov/{contrato}/{cliente}, no al revés."""
    captured_urls: list[str] = []

    async def fake_get(url: str, **kwargs: object) -> MagicMock:
        captured_urls.append(url)
        r = MagicMock()
        r.is_success = True
        return r

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = fake_get

    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        await adapter.verificar_contrato(numero_cliente="1109294", numero_contrato="0281767003")

    assert len(captured_urls) == 1
    url = captured_urls[0]
    assert "/0281767003/1109294" in url, f"Orden incorrecto en URL: {url}"
    assert "/1109294/0281767003" not in url, f"Orden invertido (bug): {url}"


async def test_devuelve_true_si_epec_responde_ok() -> None:
    mock_client = _make_client(status=200)
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        result = await adapter.verificar_contrato("1109294", "0281767003")
    assert result is True


async def test_devuelve_false_si_epec_responde_error() -> None:
    mock_client = _make_client(status=404)
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        result = await adapter.verificar_contrato("1109294", "0281767003")
    assert result is False


# ---------------------------------------------------------------------------
# obtener_documentos
# ---------------------------------------------------------------------------


async def test_obtener_documentos_retorna_lista_vacia_si_body_vacio() -> None:
    mock_client = _make_client(status=200, body=b"")
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        result = await adapter.obtener_documentos("1109294", "0281767003")
    assert result == []


async def test_obtener_documentos_parsea_lista_json() -> None:
    datos = [
        {
            "periodo": "04/2026",
            "nroComprobante": "0001-00000123",
            "importe": 15230.50,
            "fechaVencimiento": "2026-05-15",
        }
    ]
    mock_client = _make_client(status=200, json_data=datos)
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        result = await adapter.obtener_documentos("1109294", "0281767003")

    assert len(result) == 1
    assert result[0] == DocumentoPago(
        periodo="04/2026",
        nro_factura="0001-00000123",
        importe=15230.50,
        fecha_vencimiento="2026-05-15",
    )


async def test_obtener_documentos_parsea_objeto_con_clave_documentos() -> None:
    datos = {
        "documentos": [
            {
                "periodo": "05/2026",
                "nroComprobante": "0001-00000999",
                "importe": 8000.0,
                "fechaVencimiento": "2026-06-15",
            }
        ]
    }
    mock_client = _make_client(status=200, json_data=datos)
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        result = await adapter.obtener_documentos("1109294", "0281767003")

    assert len(result) == 1
    assert result[0].periodo == "05/2026"


async def test_obtener_documentos_lanza_error_si_epec_retorna_no_exitoso() -> None:
    mock_client = _make_client(status=404)
    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        with pytest.raises(ValueError, match="Contrato"):
            await adapter.obtener_documentos("1109294", "invalido")


async def test_obtener_documentos_usa_orden_contrato_cliente_en_url() -> None:
    captured_urls: list[str] = []

    async def fake_get(url: str, **kwargs: object) -> MagicMock:
        captured_urls.append(url)
        r = MagicMock()
        r.is_success = True
        r.content = b""
        return r

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = fake_get

    with patch(
        "infrastructure.epec.epec_factura_verificacion.httpx.AsyncClient", return_value=mock_client
    ):
        adapter = EpecFacturaVerificacion()
        await adapter.obtener_documentos(numero_cliente="1109294", numero_contrato="0281767003")

    assert "/0281767003/1109294" in captured_urls[0]
