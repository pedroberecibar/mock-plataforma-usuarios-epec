"""Tests para los nuevos endpoints de Sprint 8 en objetivos_router.

GET /objetivos/sugerido/{suministro_id}
GET /objetivos/{suministro_id}/estado
"""

import calendar
from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_objetivo_repo,
    get_usuario_repo,
    get_vecinos_repo,
)
from interface.objetivos_router import router

SUMINISTRO = "3037481"
TOKEN = "tok"


def build_client(
    objetivo_repo: FakeObjetivoConsumoRepository | None = None,
    consumo_repo: FakeConsumoDiarioRepository | None = None,
    vecinos_repo: FakeVecinosRepository | None = None,
) -> tuple[
    TestClient,
    FakeObjetivoConsumoRepository,
    FakeConsumoDiarioRepository,
    FakeVecinosRepository,
]:
    app = FastAPI()
    app.include_router(router)

    auth = FakeAuthProvider()
    auth._tokens[TOKEN] = "demo"
    usuario_repo = FakeUsuarioRepository({"demo": SUMINISTRO})

    o_repo = objetivo_repo or FakeObjetivoConsumoRepository()
    c_repo = consumo_repo or FakeConsumoDiarioRepository()
    v_repo = vecinos_repo or FakeVecinosRepository()

    app.dependency_overrides[get_auth_provider] = lambda: auth
    app.dependency_overrides[get_usuario_repo] = lambda: usuario_repo
    app.dependency_overrides[get_objetivo_repo] = lambda: o_repo
    app.dependency_overrides[get_consumo_repo] = lambda: c_repo
    app.dependency_overrides[get_vecinos_repo] = lambda: v_repo

    return TestClient(app), o_repo, c_repo, v_repo


# ---------------------------------------------------------------------------
# GET /objetivos/sugerido/{suministro_id}
# ---------------------------------------------------------------------------


def test_sugerido_sin_datos_cuando_no_hay_vecinos() -> None:
    client, _, _, _ = build_client()

    res = client.get(
        "/objetivos/sugerido?mes=2026-06",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["sin_datos"] is True
    assert body["valor_kwh"] is None
    assert body["n_vecinos"] == 0


async def test_sugerido_devuelve_promedio_con_cinco_vecinos() -> None:
    consumo_repo = FakeConsumoDiarioRepository()
    vecinos_repo = FakeVecinosRepository()
    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos[SUMINISTRO] = vecinos

    last_day = calendar.monthrange(2025, 6)[1]
    for vid in vecinos:
        for d in range(1, last_day + 1):
            await consumo_repo.upsert_consumo(vid, date(2025, 6, d), 200.0 / last_day)

    client, _, _, _ = build_client(consumo_repo=consumo_repo, vecinos_repo=vecinos_repo)
    res = client.get(
        "/objetivos/sugerido?mes=2026-06",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["sin_datos"] is False
    assert body["n_vecinos"] == 5
    assert body["valor_kwh"] is not None
    assert abs(body["valor_kwh"] - 200.0) < 1.0


def test_sugerido_retorna_422_con_mes_invalido() -> None:
    client, _, _, _ = build_client()
    res = client.get(
        "/objetivos/sugerido?mes=no-valido",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# GET /objetivos/{suministro_id}/estado
# ---------------------------------------------------------------------------


def test_estado_sin_objetivo() -> None:
    client, _, _, _ = build_client()
    res = client.get(
        "/objetivos/estado?mes=2026-06",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert res.status_code == 200
    assert res.json()["texto_dinamico"] == "sin_objetivo"


async def test_estado_agotado() -> None:
    objetivo_repo = FakeObjetivoConsumoRepository()
    consumo_repo = FakeConsumoDiarioRepository()
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 100.0, "manual", date(2026, 6, 1))
    # 14 días × 10 kWh = 140 kWh >= 100 → agotado; hoy=2026-06-15
    for d in range(1, 15):
        await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, d), 10.0)

    client, _, _, _ = build_client(objetivo_repo=objetivo_repo, consumo_repo=consumo_repo)
    res = client.get(
        "/objetivos/estado?mes=2026-06&hoy=2026-06-15",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["texto_dinamico"] == "agotado"
    assert body["excedente_kwh"] is not None
    assert abs(body["excedente_kwh"] - 40.0) < 0.5


async def test_estado_sobre_ritmo() -> None:
    objetivo_repo = FakeObjetivoConsumoRepository()
    consumo_repo = FakeConsumoDiarioRepository()
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 300.0, "manual", date(2026, 6, 1))
    # ritmo_diario = 10 kWh/día; hoy=2026-06-15 (15 días transcurridos)
    # 14 × 13 = 182 kWh → días_consumidos=18.2 > 15×1.05=15.75 → sobre_ritmo
    for d in range(1, 15):
        await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, d), 13.0)

    client, _, _, _ = build_client(objetivo_repo=objetivo_repo, consumo_repo=consumo_repo)
    res = client.get(
        "/objetivos/estado?mes=2026-06&hoy=2026-06-15",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    body = res.json()
    assert body["texto_dinamico"] == "sobre_ritmo"


def test_estado_retorna_422_con_mes_invalido() -> None:
    client, _, _, _ = build_client()
    res = client.get(
        "/objetivos/estado?mes=abc",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    assert res.status_code == 422
