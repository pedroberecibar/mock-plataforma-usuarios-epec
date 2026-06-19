from unittest.mock import AsyncMock, patch

import httpx
import pytest

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase


@pytest.fixture
def uc() -> ObtenerLinkFacturaUseCase:
    return ObtenerLinkFacturaUseCase(base_url="https://epec.com.ar/factura")


@pytest.fixture
def mock_httpx_get():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        yield mock_get


async def test_ejecutar_llama_api_epec_y_devuelve_base_url(
    uc: ObtenerLinkFacturaUseCase, mock_httpx_get
) -> None:  # noqa: ANN001
    url = await uc.ejecutar(numero_cliente="123456", numero_contrato="789012")

    mock_httpx_get.assert_called_once()
    args, kwargs = mock_httpx_get.call_args
    assert args[0] == "https://www.epec.com.ar/api/contratos/no-ov/123456/789012"
    assert kwargs["headers"]["apikey"] == "web-prod"

    assert url == "https://epec.com.ar/factura"


async def test_devuelve_url_por_defecto_si_base_url_es_none(mock_httpx_get) -> None:  # noqa: ANN001
    uc_sin_base = ObtenerLinkFacturaUseCase(base_url=None)
    url = await uc_sin_base.ejecutar("1", "2")
    assert url == "https://www.epec.com.ar/tramites/pagos"


async def test_levanta_error_si_httpx_falla(uc: ObtenerLinkFacturaUseCase) -> None:
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()

        def raise_err() -> None:
            raise httpx.HTTPStatusError("Error", request=AsyncMock(), response=mock_response)

        mock_response.raise_for_status = raise_err
        mock_get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await uc.ejecutar("1", "2")
