"""Wrapper de desarrollo: carga .env y lanza uvicorn.

No commitear datos de prod. Usar start-backend.ps1 en producción.
"""

import os
import sys
from pathlib import Path

_root = Path(__file__).parent.parent

# Carga .env respetando backslashes de Windows (no usa bash source)
_env_file = _root / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/plataforma_clientes.db")
os.environ.setdefault("INGEST_DESDE_INICIAL", "2026-06-01")

sys.path.insert(0, str(_root / "src"))
import uvicorn  # noqa: E402

port = int(os.environ.get("PORT", "8000"))
uvicorn.run("main:create_app", factory=True, host="0.0.0.0", port=port)
