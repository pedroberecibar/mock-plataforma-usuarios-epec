"""Tests for scripts/seed_demo.py — quarantine guard (ADR-002).

seed_demo genera consumo sintético; NUNCA debe escribir en la DB real. El guard
`assert_safe_seed_target` aborta si el destino es la DB real (o cualquier DB que no
sea SQLite descartable).

El script vive en scripts/ (fuera del pythonpath), se carga por file path. Importarlo
NO debe tener efectos colaterales (no debe sembrar ninguna DB).
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "seed_demo.py"
_spec = importlib.util.spec_from_file_location("seed_demo", _SCRIPT)
assert _spec and _spec.loader
seed_demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seed_demo)


class TestAssertSafeSeedTarget:
    def test_blocks_real_db(self) -> None:
        with pytest.raises(RuntimeError):
            seed_demo.assert_safe_seed_target("sqlite+aiosqlite:///./data/plataforma_clientes.db")

    def test_blocks_real_db_without_relative_prefix(self) -> None:
        with pytest.raises(RuntimeError):
            seed_demo.assert_safe_seed_target("sqlite+aiosqlite:///data/plataforma_clientes.db")

    def test_blocks_real_db_backups(self) -> None:
        with pytest.raises(RuntimeError):
            seed_demo.assert_safe_seed_target(
                "sqlite+aiosqlite:///data/plataforma_clientes.backup-20260626-075007.db"
            )

    def test_blocks_non_sqlite_url(self) -> None:
        with pytest.raises(RuntimeError):
            seed_demo.assert_safe_seed_target("postgresql+asyncpg://user:pass@host/prod")

    def test_allows_throwaway_db(self) -> None:
        # No debe lanzar
        seed_demo.assert_safe_seed_target("sqlite+aiosqlite:///./data/ui-dev.db")

    def test_allows_in_memory(self) -> None:
        seed_demo.assert_safe_seed_target("sqlite+aiosqlite:///:memory:")


class TestDefaultTargetIsThrowaway:
    def test_default_db_url_is_not_the_real_db(self) -> None:
        # El destino por defecto del seed debe ser una DB descartable, no la real.
        seed_demo.assert_safe_seed_target(seed_demo._resolve_db_url())
