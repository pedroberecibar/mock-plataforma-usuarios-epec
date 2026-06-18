from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from interface.dependencies import get_auth_provider, get_objetivo_repo, get_usuario_repo
from interface.objetivos_router import router


def build_client(
    objetivo_repo: FakeObjetivoConsumoRepository | None = None,
) -> tuple[TestClient, FakeObjetivoConsumoRepository]:
    app = FastAPI()
    app.include_router(router)

    auth = FakeAuthProvider()
    usuario_repo = FakeUsuarioRepository({"demo": "3037481"})
    repo = objetivo_repo or FakeObjetivoConsumoRepository()

    app.dependency_overrides[get_auth_provider] = lambda: auth
    app.dependency_overrides[get_usuario_repo] = lambda: usuario_repo
    app.dependency_overrides[get_objetivo_repo] = lambda: repo

    token = "tok"
    auth._tokens[token] = "demo"

    return TestClient(app), repo


def test_get_objetivo_returns_null_when_no_objetivo() -> None:
    client, _ = build_client()
    res = client.get("/objetivos", headers={"Authorization": "Bearer tok"})
    assert res.status_code == 200
    assert res.json() is None


async def test_get_objetivo_returns_vigente() -> None:
    repo = FakeObjetivoConsumoRepository()
    await repo.upsert_objetivo("3037481", 150.0, "manual", date(2026, 6, 1))
    client, _ = build_client(repo)

    res = client.get("/objetivos", headers={"Authorization": "Bearer tok"})

    assert res.status_code == 200
    body = res.json()
    assert body["valor_kwh"] == 150.0
    assert body["origen"] == "manual"


def test_post_objetivo_creates_and_returns_objetivo() -> None:
    client, repo = build_client()

    res = client.post(
        "/objetivos",
        json={"valor_kwh": 200.0},
        headers={"Authorization": "Bearer tok"},
    )

    assert res.status_code == 201
    body = res.json()
    assert body["valor_kwh"] == 200.0
    assert body["origen"] == "manual"


def test_post_objetivo_returns_422_for_zero_kwh() -> None:
    client, _ = build_client()

    res = client.post(
        "/objetivos",
        json={"valor_kwh": 0},
        headers={"Authorization": "Bearer tok"},
    )

    assert res.status_code == 422


def test_get_objetivo_returns_401_without_token() -> None:
    client, _ = build_client()
    res = client.get("/objetivos")
    assert res.status_code == 401
