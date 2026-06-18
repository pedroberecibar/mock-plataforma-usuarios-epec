import pytest

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase


@pytest.fixture
def uc() -> ObtenerLinkFacturaUseCase:
    return ObtenerLinkFacturaUseCase(base_url="https://epec.com.ar/factura")


async def test_construye_url_con_numero_cliente_y_contrato(uc: ObtenerLinkFacturaUseCase) -> None:
    url = await uc.ejecutar(numero_cliente="123456", numero_contrato="789012")
    assert url == "https://epec.com.ar/factura?nc=123456&ct=789012"


async def test_url_incluye_ambos_parametros(uc: ObtenerLinkFacturaUseCase) -> None:
    url = await uc.ejecutar(numero_cliente="AAA", numero_contrato="BBB")
    assert "nc=AAA" in url
    assert "ct=BBB" in url


async def test_distintos_bases_url_producen_distintas_urls() -> None:
    uc_prod = ObtenerLinkFacturaUseCase(base_url="https://epec.com.ar/factura")
    uc_test = ObtenerLinkFacturaUseCase(base_url="https://staging.epec.com.ar/factura")
    url_prod = await uc_prod.ejecutar("1", "2")
    url_test = await uc_test.ejecutar("1", "2")
    assert url_prod != url_test
    assert url_prod.startswith("https://epec.com.ar")
    assert url_test.startswith("https://staging.epec.com.ar")
