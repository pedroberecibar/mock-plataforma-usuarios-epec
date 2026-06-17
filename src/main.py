"""Composition root.

Único módulo fuera de las capas de domain/application/infrastructure/interface;
es el único lugar que conoce tanto los adapters concretos (infrastructure) como
los routers (interface) y los cablea entre sí. Ver ADR-001.
"""

import os

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.auth.jwt_auth_provider import JwtAuthProvider
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from interface.auth_router import router as auth_router
from interface.consumo_router import router as consumo_router
from interface.dependencies import get_auth_provider, get_consumo_repo


def create_app() -> FastAPI:
    app = FastAPI(title="Plataforma de Clientes EPEC")
    app.include_router(auth_router)
    app.include_router(consumo_router)

    secret_key = os.environ["SECRET_KEY"]
    app.dependency_overrides[get_auth_provider] = lambda: JwtAuthProvider(secret_key=secret_key)

    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///epec.db")
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    def _get_consumo_repo() -> SQLiteConsumoDiarioRepository:
        return SQLiteConsumoDiarioRepository(session_factory())

    app.dependency_overrides[get_consumo_repo] = _get_consumo_repo

    return app
