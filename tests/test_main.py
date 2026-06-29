import asyncio

from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, Usuario
from main import create_app

_ph = PasswordHasher()
_TEST_PASSWORD = "mi-clave-segura"


def test_create_app_wires_a_working_login_endpoint(monkeypatch, tmp_path) -> None:
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-key-that-is-long-enough")
    monkeypatch.setenv("DATABASE_URL", db_url)

    async def _seed() -> None:
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_sessionmaker(engine, class_=AsyncSession)() as session:
            session.add(
                Usuario(
                    usuario="cliente1",
                    suministro_id="3037481",
                    password_hash=_ph.hash(_TEST_PASSWORD),
                )
            )
            await session.commit()
        await engine.dispose()

    asyncio.run(_seed())

    client = TestClient(create_app())
    response = client.post("/auth/login", json={"usuario": "cliente1", "password": _TEST_PASSWORD})

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["suministro_id"] == "3037481"


def test_factura_datos_returns_503_when_oracle_not_configured(monkeypatch, tmp_path) -> None:
    """Sin Oracle (ADR-002) no se devuelve factura fake: 503 explícito, no deuda inventada."""
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-key-that-is-long-enough")
    monkeypatch.setenv("DATABASE_URL", db_url)
    for var in ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME"):
        monkeypatch.delenv(var, raising=False)

    async def _seed() -> None:
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_sessionmaker(engine, class_=AsyncSession)() as session:
            session.add(
                Usuario(
                    usuario="cliente1",
                    suministro_id="3037481",
                    password_hash=_ph.hash(_TEST_PASSWORD),
                )
            )
            await session.commit()
        await engine.dispose()

    asyncio.run(_seed())

    client = TestClient(create_app())
    login = client.post("/auth/login", json={"usuario": "cliente1", "password": _TEST_PASSWORD})
    token = login.json()["token"]

    response = client.get("/factura/datos", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 503
