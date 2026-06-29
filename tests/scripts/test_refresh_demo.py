"""Tests for scripts/refresh_demo.py — comando único de refresh de la demo (ADR-002).

refresh_demo orquesta: ingesta de 2817670 desde Oracle (seed_vecinos_reales.py) →
regeneración de fixtures (generate_mock_fixtures.py). Importarlo no debe ejecutar nada.
"""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "refresh_demo.py"
_spec = importlib.util.spec_from_file_location("refresh_demo", _SCRIPT)
assert _spec and _spec.loader
refresh_demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(refresh_demo)


class TestMissingOracleVars:
    def test_all_present_returns_empty(self) -> None:
        env = {"OR_HOST": "h", "OR_USER": "u", "OR_PASS": "p", "OR_SERVICE_NAME": "s"}
        assert refresh_demo.missing_oracle_vars(env) == []

    def test_reports_missing(self) -> None:
        env = {"OR_HOST": "h", "OR_USER": "u"}
        assert set(refresh_demo.missing_oracle_vars(env)) == {"OR_PASS", "OR_SERVICE_NAME"}

    def test_blank_counts_as_missing(self) -> None:
        env = {"OR_HOST": "h", "OR_USER": "u", "OR_PASS": "", "OR_SERVICE_NAME": "s"}
        assert refresh_demo.missing_oracle_vars(env) == ["OR_PASS"]


class TestBuildSteps:
    def test_runs_ingesta_then_fixtures_in_order(self) -> None:
        root = Path("/proj")
        steps = refresh_demo.build_steps("python", root)
        scripts = [step[-1] for step in steps]
        assert scripts == [
            str(root / "scripts" / "seed_vecinos_reales.py"),
            str(root / "scripts" / "generate_mock_fixtures.py"),
        ]

    def test_each_step_uses_given_interpreter(self) -> None:
        steps = refresh_demo.build_steps("/usr/bin/python3", Path("/proj"))
        assert all(step[0] == "/usr/bin/python3" for step in steps)
