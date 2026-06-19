"""Tests de integración HTTP para home_router."""

import asyncio
from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from domain.ports.auth_provider import AuthProvider
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.proyeccion_repository import FakeProyeccionRepository
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_proyeccion_repo,
    get_usuario_repo,
    get_vecinos_repo,
)
from interface.home_router import router as home_router

_TEST_TOKEN = "fake-token"
_TEST_SUMINISTRO = "S1"
_TEST_USUARIO = "usuario-test"


class _FakeAuth(AuthProvider):
    async def autenticar(
        self, usuario: str, password: str, password_hash: str | None = None
    ) -> str | None:
        return _TEST_TOKEN

    async def verificar_token(self, token: str) -> str | None:
        return _TEST_USUARIO if token == _TEST_TOKEN else None

    def verificar_password(self, password: str, password_hash: str) -> bool:
        return True


def _make_app(
    consumo: FakeConsumoDiarioRepository,
    vecinos: FakeVecinosRepository | None = None,
    proy: FakeProyeccionRepository | None = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(home_router)
    app.dependency_overrides[get_auth_provider] = lambda: _FakeAuth()
    app.dependency_overrides[get_usuario_repo] = lambda: FakeUsuarioRepository(
        {_TEST_USUARIO: _TEST_SUMINISTRO}
    )
    app.dependency_overrides[get_consumo_repo] = lambda: consumo
    app.dependency_overrides[get_vecinos_repo] = lambda: vecinos or FakeVecinosRepository()
    app.dependency_overrides[get_proyeccion_repo] = lambda: proy or FakeProyeccionRepository()
    return TestClient(app)


def _seed(repo: FakeConsumoDiarioRepository, sid: str, dia: date, kwh: float) -> None:
    asyncio.run(repo.upsert_consumo(sid, dia, kwh))


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------


def test_home_requiere_autenticacion() -> None:
    consumo = FakeConsumoDiarioRepository()
    client = _make_app(consumo)

    resp = client.get("/home?mes=2026-06")

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Respuesta exitosa
# ---------------------------------------------------------------------------


def test_home_devuelve_estructura_completa() -> None:
    consumo = FakeConsumoDiarioRepository()
    _seed(consumo, "S1", date(2026, 6, 1), 10.0)
    _seed(consumo, "S1", date(2026, 6, 2), 12.0)

    client = _make_app(consumo)
    resp = client.get(
        "/home?mes=2026-06",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "consumo_mes" in body
    assert "comparacion_zona" in body
    assert "proyeccion" in body
    assert "datos_hasta" in body
    assert "timestamp" in body


def test_home_consumo_mes_total() -> None:
    consumo = FakeConsumoDiarioRepository()
    _seed(consumo, "S1", date(2026, 6, 1), 10.0)
    _seed(consumo, "S1", date(2026, 6, 2), 15.0)

    client = _make_app(consumo)
    resp = client.get(
        "/home?mes=2026-06",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["consumo_mes"]["total_kwh"] == 25.0


def test_home_usa_mes_actual_si_no_se_especifica() -> None:
    consumo = FakeConsumoDiarioRepository()
    client = _make_app(consumo)

    resp = client.get(
        "/home",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200


def test_home_error_422_si_mes_invalido() -> None:
    consumo = FakeConsumoDiarioRepository()
    client = _make_app(consumo)

    resp = client.get(
        "/home?mes=2026-13",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 422


def test_home_zona_sin_vecinos() -> None:
    consumo = FakeConsumoDiarioRepository()
    _seed(consumo, "S1", date(2026, 6, 1), 10.0)
    vecinos = FakeVecinosRepository()

    client = _make_app(consumo, vecinos=vecinos)
    resp = client.get(
        "/home?mes=2026-06",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["comparacion_zona"]["n_vecinos"] == 0
    assert body["comparacion_zona"]["promedio_vecinos_kwh"] is None


def test_home_proyeccion_insuficiente_devuelve_rangos_null() -> None:
    consumo = FakeConsumoDiarioRepository()
    # Solo 3 días → método insuficiente
    for dia in range(1, 4):
        _seed(consumo, "S1", date(2026, 6, dia), 10.0)

    client = _make_app(consumo)
    resp = client.get(
        "/home?mes=2026-06",
        headers={"Authorization": "Bearer fake-token"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["proyeccion"]["metodo_aplicado"] == "insuficiente"
    assert body["proyeccion"]["rango_inferior_kwh"] is None
    assert body["proyeccion"]["rango_superior_kwh"] is None
