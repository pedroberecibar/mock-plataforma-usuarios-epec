#!/usr/bin/env python3
"""capture_decision.py — PostToolUse hook: captures *marked* decisions to the Obsidian vault.

Invoked automatically by the PostToolUse hook in ``.claude/settings.json`` after
Claude Code runs a Bash command. Reads the hook JSON payload from stdin (or a
string as argv[1] for manual use).

Refined behavior (intentional, low-noise):
- Only the **command** is inspected, never the tool output. Reading files or
  running tools whose output happens to mention "arquitectura/refactor" no longer
  triggers a capture.
- A capture happens only when the command contains an explicit marker
  ``@decision`` (or ``@adr``). The clean text after the marker is logged --
  not a raw dump of the command and its output.
- Manual use (``python scripts/capture_decision.py "..."``) logs the argument
  directly; the marker is optional there because the call is already intentional.

Usage (hook):    python scripts/capture_decision.py        # reads stdin JSON
Usage (manual):  python scripts/capture_decision.py "@decision Elegimos pytest porque..."

Never fails the hook -- always exits 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Explicit, deliberate marker. Optional ``:`` or ``=`` separator after it.
_MARKER_RE = re.compile(r"@(?:decision|adr)\s*[:=]?\s*(.*)", re.IGNORECASE)


def extract_decision(text: str | None) -> str | None:
    """Return the clean decision text if an ``@decision``/``@adr`` marker is present.

    The captured text runs from just after the marker up to the first closing
    quote or newline, so a marker embedded in an ``echo "..."`` does not drag in
    the rest of the shell command.
    """
    if not text:
        return None
    match = _MARKER_RE.search(text)
    if not match:
        return None
    rest = match.group(1)
    for stop in ('"', "'", "\n"):
        idx = rest.find(stop)
        if idx != -1:
            rest = rest[:idx]
    rest = rest.strip()
    return rest or None


def read_hook_command(raw: str) -> str:
    """Extract only the Bash command from the hook JSON payload (output ignored)."""
    if not raw or not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except Exception:
        return ""
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict):
        return str(tool_input.get("command", "") or "")
    return ""


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


def append_decision(vault_path: Path, project: str, decision_text: str) -> None:
    """Append a single clean decision line to today's session note."""
    today = date.today().isoformat()
    project_dir = vault_path / "Projects" / project
    project_dir.mkdir(parents=True, exist_ok=True)
    session_file = project_dir / f"{today}-session.md"
    if not session_file.exists():
        session_file.write_text(
            f"# Sesión {today} — {project}\n\n## Decisiones técnicas\n\n",
            encoding="utf-8",
        )
    with session_file.open("a", encoding="utf-8") as f:
        f.write(f"- {decision_text}\n")
    print(f"[capture_decision] Decisión guardada en {session_file}")


def main() -> None:
    decision: str | None
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        decision = extract_decision(sys.argv[1]) or sys.argv[1].strip()
    else:
        decision = extract_decision(read_hook_command(sys.stdin.read()))

    if not decision:
        sys.exit(0)

    vault_path = get_vault_path()
    if vault_path is None or not vault_path.exists():
        sys.exit(0)

    try:
        append_decision(vault_path, get_project_name(), decision)
    except Exception as e:
        print(f"[capture_decision] Warning: no se pudo guardar en vault: {e}")
    sys.exit(0)


if __name__ == "__main__":
    main()
