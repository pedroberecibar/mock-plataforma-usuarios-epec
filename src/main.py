"""Composition root.

Único módulo fuera de las capas de domain/application/infrastructure/interface;
es el único lugar que conoce tanto los adapters concretos (infrastructure) como
los routers (interface) y los cablea entre sí. Ver ADR-001.
"""

import os
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.auth.jwt_auth_provider import JwtAuthProvider
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository
from infrastructure.sqlite.proyeccion_repository import SQLiteProyeccionRepository
from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository
from interface.auth_router import router as auth_router
from interface.consumo_router import router as consumo_router
from interface.dependencies import (
    get_auth_provider,
    get_consumo_repo,
    get_proyeccion_repo,
    get_vecinos_repo,
)
from interface.home_router import router as home_router


def create_app() -> FastAPI:
    app = FastAPI(title="Plataforma de Clientes EPEC")
    app.include_router(auth_router)
    app.include_router(consumo_router)
    app.include_router(home_router)

    secret_key = os.environ["SECRET_KEY"]
    app.dependency_overrides[get_auth_provider] = lambda: JwtAuthProvider(secret_key=secret_key)

    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///epec.db")
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_consumo_repo() -> AsyncGenerator[SQLiteConsumoDiarioRepository, None]:
        async with session_factory() as session:
            yield SQLiteConsumoDiarioRepository(session)

    async def _get_vecinos_repo() -> AsyncGenerator[SQLiteVecinosRepository, None]:
        async with session_factory() as session:
            yield SQLiteVecinosRepository(session)

    async def _get_proyeccion_repo() -> AsyncGenerator[SQLiteProyeccionRepository, None]:
        async with session_factory() as session:
            yield SQLiteProyeccionRepository(session)

    app.dependency_overrides[get_consumo_repo] = _get_consumo_repo
    app.dependency_overrides[get_vecinos_repo] = _get_vecinos_repo
    app.dependency_overrides[get_proyeccion_repo] = _get_proyeccion_repo

    return app
