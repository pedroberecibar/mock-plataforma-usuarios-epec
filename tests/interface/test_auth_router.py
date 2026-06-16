from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from interface.auth_router import router
from interface.dependencies import get_auth_provider


def build_client(auth_provider: FakeAuthProvider) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_auth_provider] = lambda: auth_provider
    return TestClient(app)


def test_login_returns_a_token_for_valid_credentials() -> None:
    client = build_client(FakeAuthProvider(usuarios={"cliente1": "clave123"}))

    response = client.post("/auth/login", json={"usuario": "cliente1", "password": "clave123"})

    assert response.status_code == 200
    assert response.json()["token"]


def test_login_returns_401_for_invalid_credentials() -> None:
    client = build_client(FakeAuthProvider(usuarios={"cliente1": "clave123"}))

    response = client.post("/auth/login", json={"usuario": "cliente1", "password": "incorrecta"})

    assert response.status_code == 401
