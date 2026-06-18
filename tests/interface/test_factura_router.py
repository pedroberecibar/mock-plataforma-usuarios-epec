from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from interface.dependencies import get_auth_provider, get_usuario_actual
from interface.factura_router import build_router


def build_client(base_url: str | None) -> TestClient:
    app = FastAPI()
    app.include_router(build_router(epec_base_url=base_url))
    # bypass auth for these tests
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider(usuarios={"demo": "x"})
    app.dependency_overrides[get_usuario_actual] = lambda: "demo"
    return TestClient(app)


def test_devuelve_url_con_parametros_correctos() -> None:
    client = build_client("https://epec.com.ar/factura")

    response = client.get(
        "/factura/link",
        params={"numero_cliente": "123456", "numero_contrato": "789012"},
    )

    assert response.status_code == 200
    assert response.json()["url"] == "https://epec.com.ar/factura?nc=123456&ct=789012"


def test_devuelve_503_si_base_url_no_configurada() -> None:
    client = build_client(base_url=None)

    response = client.get(
        "/factura/link",
        params={"numero_cliente": "123456", "numero_contrato": "789012"},
    )

    assert response.status_code == 503


def test_devuelve_422_si_faltan_parametros() -> None:
    client = build_client("https://epec.com.ar/factura")

    response = client.get("/factura/link")

    assert response.status_code == 422
