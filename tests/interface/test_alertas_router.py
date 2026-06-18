"""Tests para GET /alertas/config y PATCH /alertas/config."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository
from interface.alertas_router import router
from interface.dependencies import get_notificacion_config_repo, get_suministro_actual


def build_client(
    suministro_id: str = "SRV-001",
    repo: FakeNotificacionConfigRepository | None = None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_suministro_actual] = lambda: suministro_id
    _repo = repo or FakeNotificacionConfigRepository()
    app.dependency_overrides[get_notificacion_config_repo] = lambda: _repo
    return TestClient(app)


def test_get_config_devuelve_todos_los_tipos_deshabilitados_por_defecto() -> None:
    client = build_client()

    response = client.get("/alertas/config")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    tipos = {item["tipo"] for item in body}
    assert tipos == {"factura_disponible", "vencimiento_proximo", "consumo_anomalo"}
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
