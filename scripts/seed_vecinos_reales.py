"""Seed de vecinos reales desde Oracle → SQLite.

Conecta a Oracle, encuentra los vecinos por subestación del suministro configurado
(GEOREF.VW_INTELIGENTES), ingesta sus mediciones y actualiza la caché de vecinos en SQLite.

Uso:
    uv run python scripts/seed_vecinos_reales.py
    uv run python scripts/seed_vecinos_reales.py --desde 2026-01-01
    uv run python scripts/seed_vecinos_reales.py --skip-if-fresh  # no re-ingesta si < 24h

Se puede llamar antes de arrancar el backend para garantizar datos disponibles
desde el primer request (ver scripts/_start_dev.py).
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

# ── bootstrap ──────────────────────────────────────────────────────────────
_root = Path(__file__).parent.parent
_env_path = _root / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

sys.path.insert(0, str(_root / "src"))

from sqlalchemy import text  # noqa: E402, I001
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase  # noqa: E402
from infrastructure.oracle.medicion_reader import OracleMedicionReader  # noqa: E402
from infrastructure.oracle.vecinos_repository import OracleVecinosRepository  # noqa: E402
from infrastructure.sqlite.consumo_diario_repository import SQLiteConsumoDiarioRepository  # noqa: E402
from infrastructure.sqlite.suministro_repository import SQLiteSuministroRepository  # noqa: E402

# ── constantes ─────────────────────────────────────────────────────────────
_ORACLE_VARS = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")
_CACHE_TTL_HORAS = 24


async def _cache_fresco(session_factory: async_sessionmaker[AsyncSession]) -> bool:
    async with session_factory() as s:
        r = await s.execute(
            text(
                "SELECT COUNT(*) FROM vecinos_cache WHERE updated_at > datetime('now', '-24 hours')"
            )
        )
        return (r.scalar() or 0) > 0


async def _persistir_cache_vecinos(
    session_factory: async_sessionmaker[AsyncSession],
    srv_codigo: str,
    vecinos: list[str],
) -> None:
    async with session_factory() as s:
        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        await s.execute(
            text("""
                INSERT INTO vecinos_cache (suministro_id, vecinos_json, updated_at)
                VALUES (:sid, :json, :ts)
                ON CONFLICT(suministro_id) DO UPDATE
                SET vecinos_json = excluded.vecinos_json, updated_at = excluded.updated_at
            """),
            {"sid": srv_codigo, "json": json.dumps(vecinos), "ts": now},
        )
        await s.commit()
    print(f"  vecinos_cache actualizado: {len(vecinos)} vecinos para {srv_codigo}")


async def _ingestar(
    session_factory: async_sessionmaker[AsyncSession],
    todos_equipos: list[str],
    desde: date,
    hasta: date,
) -> None:
    reader = OracleMedicionReader()
    async with session_factory() as s:
        consumo_repo = SQLiteConsumoDiarioRepository(s)
        suministro_repo = SQLiteSuministroRepository(s)
        resultado = await IngestarConsumoDiarioUseCase(
            reader, consumo_repo, suministro_repo
        ).ejecutar(desde, hasta, equipos=todos_equipos)
        await s.commit()
    print(
        f"  Ingesta: {resultado.suministros_procesados} suministros, "
        f"{resultado.dias_procesados} dias ({desde} a {hasta})"
    )


async def _run(desde: date, hasta: date, skip_if_fresh: bool) -> None:
    missing = [v for v in _ORACLE_VARS if not os.environ.get(v)]
    if missing:
        print(
            f"[seed_vecinos_reales] Oracle no configurado ({', '.join(missing)}) — salteando.",
            file=sys.stderr,
        )
        return

    equipos_env = os.environ.get("INGEST_EQUIPOS", "").strip()
    if not equipos_env:
        print("[seed_vecinos_reales] INGEST_EQUIPOS no definido — salteando.", file=sys.stderr)
        return

    equipos_iniciales = [e.strip() for e in equipos_env.split(",") if e.strip()]
    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data/plataforma_clientes.db")
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    if skip_if_fresh and await _cache_fresco(session_factory):
        print("[seed_vecinos_reales] Caché de vecinos fresco (< 24h) — salteando.")
        await engine.dispose()
        return

    print(f"[seed_vecinos_reales] Iniciando seed desde Oracle ({desde} a {hasta})...")

    oracle = OracleVecinosRepository()
    todos_vecino_equipos: list[str] = []

    # Resolver SRV_CODIGO de los equipos configurados
    srv_map = await oracle.resolver_srv_de_equipos(equipos_iniciales)

    for equipo in equipos_iniciales:
        srv_codigo = srv_map.get(equipo)
        if not srv_codigo:
            print(f"  [!] No se encontró SRV_CODIGO para equipo {equipo}", file=sys.stderr)
            continue

        print(f"\n[Equipo {equipo} -> SRV {srv_codigo}]")

        # Vecinos por subestación (GEOREF.VW_INTELIGENTES)
        vecinos = await oracle.get_vecinos(srv_codigo)
        print(f"  Vecinos en subestación: {len(vecinos)}")

        await _persistir_cache_vecinos(session_factory, srv_codigo, vecinos)

        if vecinos:
            veq = await oracle.get_equipos_activos_de_srvs(vecinos)
            print(f"  Equipos activos de vecinos: {len(veq)}")
            todos_vecino_equipos.extend(veq)

    todos_equipos = list(set(equipos_iniciales) | set(todos_vecino_equipos))
    print(
        f"\n[Ingestando mediciones: {len(equipos_iniciales)} propios + "
        f"{len(todos_vecino_equipos)} de vecinos = {len(todos_equipos)} total]"
    )

    try:
        await _ingestar(session_factory, todos_equipos, desde, hasta)
    except Exception as exc:
        print(f"  [!] Error en ingesta: {exc}", file=sys.stderr)
        raise

    await engine.dispose()
    print("\n[seed_vecinos_reales] Listo.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed de vecinos reales Oracle → SQLite.")
    default_desde = (date.today() - timedelta(days=90)).isoformat()
    parser.add_argument(
        "--desde", default=default_desde, help="Fecha inicio YYYY-MM-DD (default: hoy - 90 días)"
    )
    parser.add_argument(
        "--hasta", default=date.today().isoformat(), help="Fecha fin YYYY-MM-DD (default: hoy)"
    )
    parser.add_argument(
        "--skip-if-fresh", action="store_true", help="No re-ingesta si el caché tiene < 24h"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        desde = date.fromisoformat(args.desde)
        hasta = date.fromisoformat(args.hasta)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    asyncio.run(_run(desde, hasta, args.skip_if_fresh))
