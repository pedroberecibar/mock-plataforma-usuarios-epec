from fastapi.testclient import TestClient

from main import create_app


def test_create_app_wires_a_working_login_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-key-that-is-long-enough")
    client = TestClient(create_app())

    response = client.post("/auth/login", json={"usuario": "cliente1", "password": "cualquiera"})

    assert response.status_code == 200
    assert response.json()["token"]
