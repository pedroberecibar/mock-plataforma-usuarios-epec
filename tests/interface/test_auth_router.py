from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from interface.auth_router import router
from interface.dependencies import get_auth_provider, get_usuario_repo


def build_client(
    usuarios_suministros: dict[str, str],
    password_hashes: dict[str, str] | None = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider()
    app.dependency_overrides[get_usuario_repo] = lambda: FakeUsuarioRepository(
        usuarios_suministros,
        password_hashes=password_hashes,
    )
    return TestClient(app)


def test_login_returns_token_and_suministro_id_for_valid_user() -> None:
    client = build_client(
        usuarios_suministros={"demo": "3037481"},
        password_hashes={"demo": "clave"},  # FakeAuthProvider compara plaintext
    )

    response = client.post("/auth/login", json={"usuario": "demo", "password": "clave"})

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["suministro_id"] == "3037481"


def test_login_returns_401_for_user_not_in_usuarios_table() -> None:
    client = build_client(
        usuarios_suministros={},
        password_hashes={"demo": "clave"},
    )

    response = client.post("/auth/login", json={"usuario": "demo", "password": "clave"})

    assert response.status_code == 401


def test_login_returns_401_for_wrong_password() -> None:
    client = build_client(
        usuarios_suministros={"demo": "3037481"},
        password_hashes={"demo": "clave"},
    )

    response = client.post("/auth/login", json={"usuario": "demo", "password": "incorrecta"})

    assert response.status_code == 401


def test_login_returns_200_when_no_password_hash_stored() -> None:
    """Sin password_hash configurado el login es permitido (MVP: passwords son opcionales)."""
    client = build_client(
        usuarios_suministros={"demo": "3037481"},
        password_hashes={},
    )

    response = client.post("/auth/login", json={"usuario": "demo", "password": "clave"})

    assert response.status_code == 200
