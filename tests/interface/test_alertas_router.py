"""Tests para GET /alertas/config y PATCH /alertas/config y POST /alertas/evaluar-objetivo."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository
from infrastructure.fakes.notification_sender import FakeNotificationSender
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository
from interface.alertas_router import router
from interface.dependencies import (
    get_consumo_repo,
    get_email_actual,
    get_notificacion_config_repo,
    get_notification_sender,
    get_objetivo_repo,
    get_suministro_actual,
)


def build_client(
    suministro_id: str = "SRV-001",
    repo: FakeNotificacionConfigRepository | None = None,
    consumo_repo: FakeConsumoDiarioRepository | None = None,
    objetivo_repo: FakeObjetivoConsumoRepository | None = None,
    sender: FakeNotificationSender | None = None,
    email: str | None = "cliente@example.com",
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_suministro_actual] = lambda: suministro_id
    app.dependency_overrides[get_email_actual] = lambda: email
    _repo = repo or FakeNotificacionConfigRepository()
    app.dependency_overrides[get_notificacion_config_repo] = lambda: _repo
    app.dependency_overrides[get_consumo_repo] = lambda: (
        consumo_repo or FakeConsumoDiarioRepository()
    )
    app.dependency_overrides[get_objetivo_repo] = lambda: (
        objetivo_repo or FakeObjetivoConsumoRepository()
    )
    app.dependency_overrides[get_notification_sender] = lambda: sender or FakeNotificationSender()
    return TestClient(app)


def test_get_config_devuelve_todos_los_tipos_deshabilitados_por_defecto() -> None:
    client = build_client()

    response = client.get("/alertas/config")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    tipos = {item["tipo"] for item in body}
    assert tipos == {
        "factura_disponible",
        "vencimiento_proximo",
        "consumo_anomalo",
        "objetivo_superado",
    }
    assert all(not item["habilitado"] for item in body)


async def test_patch_config_habilita_tipo_y_get_devuelve_actualizado() -> None:
    repo = FakeNotificacionConfigRepository()
    client = build_client(repo=repo)

    patch_resp = client.patch(
        "/alertas/config",
        json={"tipo": "factura_disponible", "habilitado": True},
    )
    assert patch_resp.status_code == 200

    get_resp = client.get("/alertas/config")
    items = get_resp.json()
    factura_item = next(i for i in items if i["tipo"] == "factura_disponible")
    assert factura_item["habilitado"] is True


def test_patch_config_devuelve_422_para_tipo_invalido() -> None:
    client = build_client()

    response = client.patch(
        "/alertas/config",
        json={"tipo": "tipo_inventado", "habilitado": True},
    )

    assert response.status_code == 422


def test_get_config_requiere_suministro_actual() -> None:
    app = FastAPI()
    app.include_router(router)
    # No override for get_suministro_actual → dependency raises NotImplementedError
    app.dependency_overrides[get_notificacion_config_repo] = lambda: (
        FakeNotificacionConfigRepository()
    )
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/alertas/config")

    assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /alertas/evaluar-objetivo
# ---------------------------------------------------------------------------


def test_evaluar_objetivo_devuelve_200_sin_objetivo_configurado() -> None:
    client = build_client()

    response = client.post("/alertas/evaluar-objetivo")

    assert response.status_code == 200
    assert response.json()["evaluado"] is True


async def test_evaluar_objetivo_no_envia_si_consumo_bajo_threshold() -> None:
    from datetime import date

    objetivo_repo = FakeObjetivoConsumoRepository()
    await objetivo_repo.upsert_objetivo("SRV-001", 200.0, "manual", date(2026, 6, 1))
    consumo_repo = FakeConsumoDiarioRepository()
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 15), 100.0)  # 50%, bajo threshold
    sender = FakeNotificationSender()

    client = build_client(objetivo_repo=objetivo_repo, consumo_repo=consumo_repo, sender=sender)
    response = client.post("/alertas/evaluar-objetivo")

    assert response.status_code == 200
    assert not sender.emails_enviados


async def test_evaluar_objetivo_envia_si_consumo_supera_threshold() -> None:
    from datetime import date

    objetivo_repo = FakeObjetivoConsumoRepository()
    await objetivo_repo.upsert_objetivo("SRV-001", 200.0, "manual", date(2026, 6, 1))
    consumo_repo = FakeConsumoDiarioRepository()
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 15), 180.0)  # 90%
    sender = FakeNotificationSender()
    notif_repo = FakeNotificacionConfigRepository()
    await notif_repo.upsert_config("SRV-001", "objetivo_superado", habilitado=True)

    client = build_client(
        objetivo_repo=objetivo_repo,
        consumo_repo=consumo_repo,
        sender=sender,
        repo=notif_repo,
    )
    response = client.post("/alertas/evaluar-objetivo")

    assert response.status_code == 200
    assert len(sender.emails_enviados) == 1
    assert "objetivo" in sender.emails_enviados[0]["asunto"].lower()
