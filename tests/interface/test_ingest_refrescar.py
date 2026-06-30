"""Tests de integración HTTP para POST /ingest/refrescar (botón Actualizar)."""

import asyncio
from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_poblar_use_case,
    get_suministro_actual,
    get_usuario_repo,
)
from interface.ingest_router import router as ingest_router


class _FakePoblar:
    """Registra cómo fue invocado el use case de poblado."""

    def __init__(self) -> None:
        self.llamado_con: list[tuple[str, bool]] = []

    async def ejecutar(self, suministro_id: str, forzar: bool = False) -> None:
        self.llamado_con.append((suministro_id, forzar))


def _make_app(
    poblar: _FakePoblar,
    consumo_repo: FakeConsumoDiarioRepository,
    suministro_id: str = "SRV-001",
) -> TestClient:
    app = FastAPI()
    app.include_router(ingest_router)
    app.dependency_overrides[get_suministro_actual] = lambda: suministro_id
    app.dependency_overrides[get_consumo_repo] = lambda: consumo_repo
    app.dependency_overrides[get_poblar_use_case] = lambda: poblar
    return TestClient(app, raise_server_exceptions=False)


def test_refrescar_fuerza_ingesta_y_devuelve_datos_hasta() -> None:
    repo = FakeConsumoDiarioRepository()
    asyncio.run(repo.upsert_consumo("SRV-001", date(2026, 6, 28), 11.0))
    poblar = _FakePoblar()
    client = _make_app(poblar, repo)

    resp = client.post("/ingest/refrescar")

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["datos_hasta"] == "2026-06-28"
    # El botón Actualizar debe forzar el bypass del chequeo de frescura.
    assert poblar.llamado_con == [("SRV-001", True)]


def test_refrescar_sin_datos_devuelve_datos_hasta_null() -> None:
    repo = FakeConsumoDiarioRepository()
    poblar = _FakePoblar()
    client = _make_app(poblar, repo)

    resp = client.post("/ingest/refrescar")

    assert resp.status_code == 200
    assert resp.json()["datos_hasta"] is None


def test_refrescar_requiere_auth() -> None:
    app = FastAPI()
    app.include_router(ingest_router)
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider()
    app.dependency_overrides[get_usuario_repo] = lambda: FakeUsuarioRepository({})
    app.dependency_overrides[get_consumo_repo] = lambda: FakeConsumoDiarioRepository()
    app.dependency_overrides[get_poblar_use_case] = lambda: _FakePoblar()
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.post("/ingest/refrescar")

    assert resp.status_code == 401
