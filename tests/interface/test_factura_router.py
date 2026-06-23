from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from domain.documento_pago import DocumentoPago
from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.factura_verificacion_port import FakeFacturaVerificacionPort
from interface.dependencies import get_auth_provider, get_factura_verificacion, get_usuario_actual
from interface.factura_router import build_router

_DOC = DocumentoPago(
    periodo="04/2026",
    nro_factura="0001-00000123",
    importe=15230.50,
    fecha_vencimiento="2026-05-15",
)


def build_client(
    base_url: str | None = "https://epec.com.ar/factura",
    documentos: list[DocumentoPago] | None = None,
    contrato_invalido: bool = False,
) -> TestClient:
    app = FastAPI()
    app.include_router(build_router(epec_base_url=base_url))
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider(usuarios={"demo": "x"})
    app.dependency_overrides[get_usuario_actual] = lambda: "demo"
    app.dependency_overrides[get_factura_verificacion] = lambda: FakeFacturaVerificacionPort(
        documentos=documentos,
        contrato_invalido=contrato_invalido,
    )
    return TestClient(app)


def test_devuelve_url_correctamente() -> None:
    client = build_client("https://epec.com.ar/factura")

    with patch("interface.factura_router.ObtenerLinkFacturaUseCase") as mock_uc:
        mock_instance = mock_uc.return_value
        mock_instance.ejecutar = AsyncMock(return_value="https://epec.com.ar/factura")

        response = client.get(
            "/factura/link",
            params={"numero_cliente": "123456", "numero_contrato": "789012"},
        )

        assert response.status_code == 200
        assert response.json()["url"] == "https://epec.com.ar/factura"


def test_devuelve_503_si_epec_falla() -> None:
    client = build_client("https://epec.com.ar/factura")

    with patch("interface.factura_router.ObtenerLinkFacturaUseCase") as mock_uc:
        mock_instance = mock_uc.return_value
        mock_instance.ejecutar = AsyncMock(side_effect=Exception("API caída"))

        response = client.get(
            "/factura/link",
            params={"numero_cliente": "123456", "numero_contrato": "789012"},
        )

        assert response.status_code == 503
        assert response.json()["detail"] == "Servicio de facturación no disponible"


def test_devuelve_422_si_faltan_parametros() -> None:
    client = build_client("https://epec.com.ar/factura")

    response = client.get("/factura/link")

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /factura/documentos
# ---------------------------------------------------------------------------


def test_documentos_retorna_lista_de_documentos() -> None:
    client = build_client(documentos=[_DOC])

    response = client.get(
        "/factura/documentos",
        params={"numero_cliente": "1109294", "numero_contrato": "0281767003"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["periodo"] == "04/2026"
    assert data[0]["nro_factura"] == "0001-00000123"
    assert data[0]["importe"] == 15230.50
    assert data[0]["fecha_vencimiento"] == "2026-05-15"


def test_documentos_retorna_lista_vacia_si_no_hay_facturas() -> None:
    client = build_client(documentos=[])

    response = client.get(
        "/factura/documentos",
        params={"numero_cliente": "1109294", "numero_contrato": "0281767003"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_documentos_retorna_422_si_contrato_invalido() -> None:
    client = build_client(contrato_invalido=True)

    response = client.get(
        "/factura/documentos",
        params={"numero_cliente": "1109294", "numero_contrato": "invalido"},
    )

    assert response.status_code == 422


def test_documentos_retorna_422_si_faltan_parametros() -> None:
    client = build_client()

    response = client.get("/factura/documentos")

    assert response.status_code == 422


def test_documentos_retorna_503_si_excepcion_inesperada() -> None:
    client = build_client()

    with patch("interface.factura_router.ObtenerDocumentosFacturaUseCase") as mock_uc:
        mock_instance = mock_uc.return_value
        mock_instance.ejecutar = AsyncMock(side_effect=Exception("fallo de red"))

        response = client.get(
            "/factura/documentos",
            params={"numero_cliente": "1109294", "numero_contrato": "0281767003"},
        )

    assert response.status_code == 503
