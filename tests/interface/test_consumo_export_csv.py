"""Tests de integración para el endpoint GET /consumo/{id}/export/csv."""

from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from domain.ports.auth_provider import AuthProvider
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from interface.consumo_router import router
from interface.dependencies import get_auth_provider, get_consumo_repo


class _FakeAuth(AuthProvider):
    async def autenticar(self, usuario: str, password: str) -> str | None:
        return "fake-token"

    async def verificar_token(self, token: str) -> str | None:
        return "usuario-test" if token == "fake-token" else None

    def verificar_password(self, password: str, password_hash: str) -> bool:
        return True


def _make_app(repo: FakeConsumoDiarioRepository) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_auth_provider] = lambda: _FakeAuth()
    app.dependency_overrides[get_consumo_repo] = lambda: repo
    return TestClient(app)


@pytest.fixture
def repo_con_datos() -> FakeConsumoDiarioRepository:
    import asyncio

    repo = FakeConsumoDiarioRepository()
    asyncio.run(repo.upsert_consumo("SRV-001", date(2026, 6, 1), 12.5))
    asyncio.run(repo.upsert_consumo("SRV-001", date(2026, 6, 2), 9.8))
    return repo


def test_export_csv_content_type(repo_con_datos: FakeConsumoDiarioRepository) -> None:
    client = _make_app(repo_con_datos)
    resp = client.get(
        "/consumo/SRV-001/export/csv?desde=2026-06-01&hasta=2026-06-30",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_export_csv_formato(repo_con_datos: FakeConsumoDiarioRepository) -> None:
    client = _make_app(repo_con_datos)
    resp = client.get(
        "/consumo/SRV-001/export/csv?desde=2026-06-01&hasta=2026-06-30",
        headers={"Authorization": "Bearer fake-token"},
    )
    lines = resp.text.strip().split("\n")
    assert lines[0] == "fecha,kwh"
    assert lines[1] == "2026-06-01,12.5"
    assert lines[2] == "2026-06-02,9.8"


def test_export_csv_requiere_auth() -> None:
    repo = FakeConsumoDiarioRepository()
    client = _make_app(repo)
    resp = client.get("/consumo/SRV-001/export/csv?desde=2026-06-01&hasta=2026-06-30")
    assert resp.status_code == 401
