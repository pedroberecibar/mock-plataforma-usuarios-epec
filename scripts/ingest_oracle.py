"""Backfill manual de consumo diario desde Oracle.

Uso:
    uv run python scripts/ingest_oracle.py --desde 2025-01-01 --hasta 2026-06-17

Lee credenciales desde el entorno. Si existe un archivo .env en la raíz del
proyecto y python-dotenv está disponible, lo carga automáticamente.
"""

import argparse
import asyncio
import os
import sys
from datetime import date
from pathlib import Path

# Carga .env si existe y python-dotenv está disponible
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(_env_path)
    except ImportError:
        pass

# Agrega src/ al path para poder importar los módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase  # noqa: E402
from infrastructure.oracle.medicion_reader import OracleMedicionReader  # noqa: E402
from infrastructure.sqlite.consumo_diario_repository import (  # noqa: E402
    SQLiteConsumoDiarioRepository,
)
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository  # noqa: E402

_ORACLE_VARS = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingestar consumo diario desde Oracle a SQLite.")
    parser.add_argument("--desde", required=True, help="Fecha inicio YYYY-MM-DD")
    parser.add_argument("--hasta", required=True, help="Fecha fin YYYY-MM-DD")
    return parser.parse_args()


async def _run(desde: date, hasta: date) -> None:
    missing = [v for v in _ORACLE_VARS if not os.environ.get(v)]
    if missing:
        print(
            f"Error: variables de entorno Oracle no definidas: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    reader = OracleMedicionReader()

    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data/plataforma_clientes.db")
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        consumo_repo = SQLiteConsumoDiarioRepository(session)
        suministro_repo = SQLiteSuministroRepository(session)
        resultado = await IngestarConsumoDiarioUseCase(
            reader, consumo_repo, suministro_repo
        ).ejecutar(desde, hasta)
        await session.commit()

    await engine.dispose()
    print(
        f"Ingesta completada: {resultado.suministros_procesados} suministros, "
        f"{resultado.dias_procesados} días."
    )


def main() -> None:
    args = _parse_args()
    try:
        desde = date.fromisoformat(args.desde)
        hasta = date.fromisoformat(args.hasta)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_run(desde, hasta))


if __name__ == "__main__":
    main()
