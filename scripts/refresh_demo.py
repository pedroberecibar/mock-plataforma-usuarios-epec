"""Refresh del snapshot de la demo `mock-platform` (ADR-002).

Comando único — la máquina del owner es la única con acceso a Oracle (interno):
  1. Ingesta 2817670 + vecinos por subestación desde Oracle  (seed_vecinos_reales.py)
  2. Regenera los JSON estáticos de la demo                   (generate_mock_fixtures.py)

Después: commiteá `frontend/public/mock-data/` y `git push origin main`
(el workflow `deploy-demo.yml` buildea y publica a la rama `mock-platform`).

Uso:
    uv run python scripts/refresh_demo.py

Detalle del pipeline y bloqueos conocidos: docs/RUNBOOK-deploy-mock-platform.md
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_ORACLE_VARS = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")


def _load_dotenv(root: Path) -> None:
    """Carga .env respetando backslashes de Windows (sin pisar lo ya seteado)."""
    env_file = root / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def missing_oracle_vars(env: Mapping[str, str]) -> list[str]:
    """Devuelve las variables Oracle ausentes o vacías."""
    return [v for v in _ORACLE_VARS if not env.get(v)]


def build_steps(python_exe: str, root: Path) -> list[list[str]]:
    """Comandos a ejecutar, en orden: ingesta real → regeneración de fixtures."""
    return [
        [python_exe, str(root / "scripts" / "seed_vecinos_reales.py")],
        [python_exe, str(root / "scripts" / "generate_mock_fixtures.py")],
    ]


def main() -> int:
    _load_dotenv(_ROOT)

    missing = missing_oracle_vars(os.environ)
    if missing:
        print(
            f"[refresh_demo] Oracle no configurado ({', '.join(missing)}). "
            "Este comando solo corre en la máquina del owner con acceso a Oracle.",
            file=sys.stderr,
        )
        return 1

    for cmd in build_steps(sys.executable, _ROOT):
        print(f"\n[refresh_demo] → {' '.join(cmd)}", flush=True)
        result = subprocess.run(cmd, env=os.environ)
        if result.returncode != 0:
            print(
                f"[refresh_demo] Falló: {' '.join(cmd)} (exit {result.returncode})",
                file=sys.stderr,
            )
            return result.returncode

    print(
        "\n[refresh_demo] Snapshot regenerado. Próximo paso:\n"
        "  git add frontend/public/mock-data/\n"
        '  git commit -m "chore(demo): refresh snapshot 2817670"\n'
        "  git push origin main      # dispara deploy-demo.yml → rama mock-platform"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
