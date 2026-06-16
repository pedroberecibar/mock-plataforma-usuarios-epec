#!/usr/bin/env python3
"""capture_decision.py — PostToolUse hook: captures technical decisions to the Obsidian vault.

Invoked automatically by the PostToolUse hook in ``.claude/settings.json``
after Claude Code runs a Bash command. Reads the hook JSON payload from
stdin (or a string as argv[1] for manual use), and if the text looks like a
technical decision, appends it to today's session note in the vault.

Usage (hook):    python scripts/capture_decision.py        # reads stdin JSON
Usage (manual):  python scripts/capture_decision.py "Elegimos pytest porque..."

Never fails the hook — always exits 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

DECISION_KEYWORDS = [
    r"\belegi(mos|r|ó)\b",
    r"\bdecidi(mos|r|ó)\b",
    r"\b(por|porque) (eso|esto|tanto)\b",
    r"\bventaja\b",
    r"\bdesventaja\b",
    r"\btrade.?off\b",
    r"\bpatrón\b",
    r"\barquitectura\b",
    r"\brefactor\b",
    r"\bmigr(ar|amos|ación)\b",
    r"\bdescart(ar|amos)\b",
    r"\badr\b",
]
DECISION_RE = re.compile("|".join(DECISION_KEYWORDS), re.IGNORECASE)
MAX_OUTPUT_CHARS = 2000


def read_hook_text() -> str:
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        return sys.argv[1]
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return ""
        payload = json.loads(raw)
    except Exception:
        return ""
    parts: list[str] = []
    ti = payload.get("tool_input", {})
    if isinstance(ti, dict) and ti.get("command"):
        parts.append(str(ti["command"]))
    tr = payload.get("tool_response")
    if isinstance(tr, dict):
        for key in ("stdout", "stderr", "output", "content"):
            value = tr.get(key)
            if value:
                parts.append(str(value))
    elif isinstance(tr, str):
        parts.append(tr)
    return "\n".join(parts)


def looks_like_decision(text: str) -> bool:
    return bool(DECISION_RE.search(text))


def get_vault_path() -> Path | None:
    vault = os.environ.get("VAULT_PATH")
    if vault:
        return Path(vault)
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("VAULT_PATH="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return Path(value)
    return None


def get_project_name() -> str:
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip()).name
    except Exception:
        return Path.cwd().name


def append_to_vault(vault_path: Path, project: str, content: str) -> None:
    today = date.today().isoformat()
    project_dir = vault_path / "Projects" / project
    project_dir.mkdir(parents=True, exist_ok=True)
    session_file = project_dir / f"{today}-session.md"
    if not session_file.exists():
        session_file.write_text(
            f"# Sesión {today} — {project}\n\n## Decisiones técnicas\n\n",
            encoding="utf-8",
        )
    truncated = content[:MAX_OUTPUT_CHARS]
    if len(content) > MAX_OUTPUT_CHARS:
        truncated += f"\n... (truncado, {len(content) - MAX_OUTPUT_CHARS} chars más)"
    with session_file.open("a", encoding="utf-8") as f:
        f.write("\n---\n")
        f.write(f"**Capturado automáticamente ({today}):**\n\n")
        f.write(f"```\n{truncated}\n```\n")
    print(f"[capture_decision] Decisión guardada en {session_file}")


def main() -> None:
    output = read_hook_text()
    if not output.strip() or not looks_like_decision(output):
        sys.exit(0)
    vault_path = get_vault_path()
    if vault_path is None or not vault_path.exists():
        sys.exit(0)
    try:
        append_to_vault(vault_path, get_project_name(), output)
    except Exception as e:
        print(f"[capture_decision] Warning: no se pudo guardar en vault: {e}")
    sys.exit(0)


if __name__ == "__main__":
    main()
