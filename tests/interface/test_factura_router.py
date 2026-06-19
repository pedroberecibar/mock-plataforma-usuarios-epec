from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.factura_verificacion_port import FakeFacturaVerificacionPort
from interface.dependencies import get_auth_provider, get_factura_verificacion, get_usuario_actual
from interface.factura_router import build_router


def build_client(base_url: str | None) -> TestClient:
    app = FastAPI()
    app.include_router(build_router(epec_base_url=base_url))
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider(usuarios={"demo": "x"})
    app.dependency_overrides[get_usuario_actual] = lambda: "demo"
    app.dependency_overrides[get_factura_verificacion] = lambda: FakeFacturaVerificacionPort()
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
