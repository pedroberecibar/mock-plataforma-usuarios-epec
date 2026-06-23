"""Tests de integración HTTP para consumo_router."""

import asyncio
from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.consumo_horario_repository import FakeConsumoHorarioRepository
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository
from interface.consumo_router import router as consumo_router
from interface.dependencies import (
    get_auth_provider,
    get_consumo_horario_repo,
    get_consumo_repo,
    get_suministro_actual,
    get_usuario_repo,
    get_vecinos_repo,
)


def _make_app(repo: FakeConsumoDiarioRepository, suministro_id: str = "S1") -> TestClient:
    app = FastAPI()
    app.include_router(consumo_router)
    app.dependency_overrides[get_suministro_actual] = lambda: suministro_id
    app.dependency_overrides[get_consumo_repo] = lambda: repo
    app.dependency_overrides[get_consumo_horario_repo] = lambda: FakeConsumoHorarioRepository()
    app.dependency_overrides[get_vecinos_repo] = lambda: FakeVecinosRepository()
    return TestClient(app)


def _make_auth_app(repo: FakeConsumoDiarioRepository) -> TestClient:
    """App con cadena de auth completa — para verificar que los endpoints requieren token."""
    app = FastAPI()
    app.include_router(consumo_router)
    app.dependency_overrides[get_auth_provider] = lambda: FakeAuthProvider()
    app.dependency_overrides[get_usuario_repo] = lambda: FakeUsuarioRepository({})
    app.dependency_overrides[get_consumo_repo] = lambda: repo
    return TestClient(app)


async def _upsert(
    repo: FakeConsumoDiarioRepository, suministro_id: str, fecha: date, kwh: float
) -> None:
    await repo.upsert_consumo(suministro_id, fecha, kwh)


# ---------------------------------------------------------------------------
# GET /consumo/diario  (antes /{suministro_id}/diario — IDOR corregido)
# ---------------------------------------------------------------------------


def test_diario_devuelve_serie_y_datos_hasta() -> None:
    repo = FakeConsumoDiarioRepository()
    asyncio.run(_upsert(repo, "S1", date(2026, 6, 1), 10.0))
    asyncio.run(_upsert(repo, "S1", date(2026, 6, 2), 12.0))

    client = _make_app(repo)
    resp = client.get("/consumo/diario?desde=2026-06-01&hasta=2026-06-02")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["serie"]) == 2
    assert body["serie"][0] == {"fecha": "2026-06-01", "kwh": 10.0}
    assert body["datos_hasta"] == "2026-06-02"


def test_diario_requiere_autenticacion() -> None:
    client = _make_auth_app(FakeConsumoDiarioRepository())
    resp = client.get("/consumo/diario?desde=2026-06-01&hasta=2026-06-30")
    assert resp.status_code == 401


def test_diario_serie_vacia_cuando_no_hay_datos() -> None:
    repo = FakeConsumoDiarioRepository()
    client = _make_app(repo)

    resp = client.get("/consumo/diario?desde=2026-06-01&hasta=2026-06-30")

    assert resp.status_code == 200
    body = resp.json()
    assert body["serie"] == []
    assert body["datos_hasta"] is None


def test_diario_usa_suministro_del_jwt_no_de_la_url() -> None:
    """El suministro proviene del JWT (get_suministro_actual), no de la URL."""
    repo = FakeConsumoDiarioRepository()
    asyncio.run(_upsert(repo, "S-CORRECTO", date(2026, 6, 1), 42.0))

    client = _make_app(repo, suministro_id="S-CORRECTO")
    resp = client.get("/consumo/diario?desde=2026-06-01&hasta=2026-06-01")

    assert resp.status_code == 200
    assert resp.json()["serie"][0]["kwh"] == 42.0


# ---------------------------------------------------------------------------
# GET /consumo/comparacion  (antes /{suministro_id}/comparacion — IDOR corregido)
# ---------------------------------------------------------------------------


def test_comparacion_devuelve_tres_periodos() -> None:
    repo = FakeConsumoDiarioRepository()
    asyncio.run(_upsert(repo, "S1", date(2026, 6, 1), 10.0))
    asyncio.run(_upsert(repo, "S1", date(2026, 5, 1), 8.0))
    asyncio.run(_upsert(repo, "S1", date(2025, 6, 1), 12.0))

    client = _make_app(repo)
    resp = client.get("/consumo/comparacion?mes=2026-06")

    assert resp.status_code == 200
    body = resp.json()
    assert body["mes_actual"]["mes"] == "2026-06-01"
    assert body["mes_anterior"]["mes"] == "2026-05-01"
    assert body["mismo_mes_anio_anterior"]["mes"] == "2025-06-01"
    assert "datos_hasta" in body


def test_comparacion_requiere_autenticacion() -> None:
    client = _make_auth_app(FakeConsumoDiarioRepository())
    resp = client.get("/consumo/comparacion?mes=2026-06")
    assert resp.status_code == 401


def test_comparacion_periodo_sin_datos_devuelve_serie_vacia_y_total_null() -> None:
    repo = FakeConsumoDiarioRepository()
    asyncio.run(_upsert(repo, "S1", date(2026, 6, 1), 10.0))

    client = _make_app(repo)
    resp = client.get("/consumo/comparacion?mes=2026-06")

    assert resp.status_code == 200
    body = resp.json()
    assert body["mes_anterior"]["serie"] == []
    assert body["mes_anterior"]["total_kwh"] is None


# ---------------------------------------------------------------------------
# GET /consumo/horario
# ---------------------------------------------------------------------------


def _make_horario_app(
    horario_repo: FakeConsumoHorarioRepository, suministro_id: str = "S1"
) -> TestClient:
    app = FastAPI()
    app.include_router(consumo_router)
    app.dependency_overrides[get_suministro_actual] = lambda: suministro_id
    app.dependency_overrides[get_consumo_repo] = lambda: FakeConsumoDiarioRepository()
    app.dependency_overrides[get_consumo_horario_repo] = lambda: horario_repo
    app.dependency_overrides[get_vecinos_repo] = lambda: FakeVecinosRepository()
    return TestClient(app)


async def _upsert_horario(
    repo: FakeConsumoHorarioRepository,
    suministro_id: str,
    fecha: date,
    hora: int,
    kwh: float,
) -> None:
    await repo.upsert_consumo_horario(suministro_id, fecha, hora, kwh)


def test_horario_devuelve_serie_ordenada_por_hora() -> None:
    repo = FakeConsumoHorarioRepository()
    asyncio.run(_upsert_horario(repo, "S1", date(2026, 6, 10), 20, 0.9))
    asyncio.run(_upsert_horario(repo, "S1", date(2026, 6, 10), 8, 0.3))

    client = _make_horario_app(repo)
    resp = client.get("/consumo/horario?fecha=2026-06-10")

    assert resp.status_code == 200
    body = resp.json()
    assert body["fecha"] == "2026-06-10"
    horas = [p["hora"] for p in body["serie"]]
    assert horas == sorted(horas)
    assert len(body["serie"]) == 2


def test_horario_fecha_sin_datos_devuelve_serie_vacia() -> None:
    repo = FakeConsumoHorarioRepository()
    client = _make_horario_app(repo)
    resp = client.get("/consumo/horario?fecha=2026-06-10")
    assert resp.status_code == 200
    assert resp.json()["serie"] == []


# ---------------------------------------------------------------------------
# GET /consumo/hora-pico
# ---------------------------------------------------------------------------


def test_hora_pico_retorna_hora_correcta() -> None:
    repo = FakeConsumoHorarioRepository()
    for d in (date(2026, 6, 1), date(2026, 6, 2)):
        asyncio.run(_upsert_horario(repo, "S1", d, 20, 0.9))
        asyncio.run(_upsert_horario(repo, "S1", d, 8, 0.3))

    client = _make_horario_app(repo)
    resp = client.get("/consumo/hora-pico?mes=2026-06")

    assert resp.status_code == 200
    body = resp.json()
    assert body["hora_pico"] == 20
    assert len(body["perfil_24h"]) == 24


def test_hora_pico_sin_datos_retorna_null() -> None:
    repo = FakeConsumoHorarioRepository()
    client = _make_horario_app(repo)
    resp = client.get("/consumo/hora-pico?mes=2026-06")
    assert resp.status_code == 200
    assert resp.json() is None


def test_hora_pico_mes_formato_invalido_retorna_422() -> None:
    repo = FakeConsumoHorarioRepository()
    client = _make_horario_app(repo)
    resp = client.get("/consumo/hora-pico?mes=junio-2026")
    assert resp.status_code == 422
