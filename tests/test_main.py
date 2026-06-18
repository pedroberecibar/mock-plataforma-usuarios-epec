import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, Usuario
from main import create_app


def test_create_app_wires_a_working_login_endpoint(monkeypatch, tmp_path) -> None:
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-key-that-is-long-enough")
    monkeypatch.setenv("DATABASE_URL", db_url)

    async def _seed() -> None:
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_sessionmaker(engine, class_=AsyncSession)() as session:
            session.add(Usuario(usuario="cliente1", suministro_id="3037481"))
            await session.commit()
        await engine.dispose()

    asyncio.run(_seed())

    client = TestClient(create_app())
    response = client.post("/auth/login", json={"usuario": "cliente1", "password": "cualquiera"})

    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["suministro_id"] == "3037481"
