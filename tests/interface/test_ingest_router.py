"""Tests de integración HTTP para ingest_router."""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from domain.ports.auth_provider import AuthProvider
from domain.ports.medicion_source_reader import MedicionSourceReader
from domain.ports.suministro_repository import SuministroRepository
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.medicion_source_reader import FakeMedicionSourceReader
from infrastructure.fakes.suministro_repository import FakeSuministroRepository
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_medicion_reader,
    get_suministro_repo,
)
from interface.ingest_router import router as ingest_router


class _FakeAuth(AuthProvider):
    async def autenticar(self, usuario: str, password: str) -> str | None:
        return "fake-token"

    async def verificar_token(self, token: str) -> str | None:
        return "usuario-test" if token == "fake-token" else None


def _make_app(
    reader: MedicionSourceReader | None = None,
    suministro_repo: SuministroRepository | None = None,
    consumo_repo: FakeConsumoDiarioRepository | None = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(ingest_router)
    app.dependency_overrides[get_auth_provider] = lambda: _FakeAuth()
    app.dependency_overrides[get_consumo_repo] = lambda: (
        consumo_repo or FakeConsumoDiarioRepository()
    )
    app.dependency_overrides[get_suministro_repo] = lambda: (
        suministro_repo or FakeSuministroRepository()
    )
    if reader is not None:
        app.dependency_overrides[get_medicion_reader] = lambda: reader
    else:

        def _raise_503() -> None:
            raise HTTPException(
                status_code=503,
                detail="Oracle no configurado — definir OR_HOST, OR_USER, OR_PASS, OR_SERVICE_NAME",
            )

        app.dependency_overrides[get_medicion_reader] = _raise_503
    return TestClient(app, raise_server_exceptions=False)


def test_ingest_requiere_autenticacion() -> None:
    client = _make_app(reader=FakeMedicionSourceReader())
    resp = client.post("/ingest/consumo?desde=2026-06-01&hasta=2026-06-17")
    assert resp.status_code == 401


def test_ingest_exitoso_devuelve_ok() -> None:
    from datetime import date

    from domain.lecturas import LecturaTelemedida

    lecturas = [
        LecturaTelemedida("E1", "SRV-1", "E", date(2026, 6, 1), 1000.0),
        LecturaTelemedida("E1", "SRV-1", "E", date(2026, 6, 5), 1040.0),
    ]
    reader = FakeMedicionSourceReader(lecturas=lecturas)
    client = _make_app(reader=reader)

    resp = client.post(
        "/ingest/consumo?desde=2026-06-01&hasta=2026-06-05",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "suministros_procesados" in body
    assert "dias_procesados" in body


def test_ingest_503_si_oracle_no_configurado() -> None:
    client = _make_app(reader=None)

    resp = client.post(
        "/ingest/consumo?desde=2026-06-01&hasta=2026-06-17",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 503
