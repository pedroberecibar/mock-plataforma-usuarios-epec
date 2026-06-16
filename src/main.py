"""Composition root.

Único módulo fuera de las capas de domain/application/infrastructure/interface;
es el único lugar que conoce tanto los adapters concretos (infrastructure) como
los routers (interface) y los cablea entre sí. Ver ADR-001.
"""

import os

from fastapi import FastAPI

from infrastructure.auth.jwt_auth_provider import JwtAuthProvider
from interface.auth_router import router as auth_router
from interface.dependencies import get_auth_provider


def create_app() -> FastAPI:
    app = FastAPI(title="Plataforma de Clientes EPEC")
    app.include_router(auth_router)

    secret_key = os.environ["SECRET_KEY"]
    app.dependency_overrides[get_auth_provider] = lambda: JwtAuthProvider(secret_key=secret_key)

    return app
