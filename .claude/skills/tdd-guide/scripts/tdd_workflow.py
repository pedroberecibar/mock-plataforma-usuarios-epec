#!/usr/bin/env python3
"""tdd_workflow.py — TDD phase validator (PreToolUse hook).

Reads the Claude Code PreToolUse JSON payload from stdin (or accepts
--check PATH for manual use) and, for backend Python source files under
``src/``, verifies a corresponding test exists and is currently RED.

Scope: only enforces on ``*.py`` files under a ``src/`` directory. Every
other file (frontend, config, docs, tests themselves) is allowed through.

Exit codes (Claude Code hook contract):
    0 — allow the tool call
    2 — block the tool call (stderr is shown to Claude)
Any unexpected error fails open (exit 0): the hook never bricks editing.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def resolve_target() -> str | None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--check")
    args, _ = parser.parse_known_args()
    if args.check:
        return args.check
    # Hook mode: read the JSON payload from stdin.
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        payload = json.loads(raw)
        return payload.get("tool_input", {}).get("file_path")
    except Exception:
        return None


def is_backend_source(path: Path) -> bool:
    if path.suffix != ".py":
        return False
    parts = path.parts
    if "tests" in parts or path.name.startswith("test_"):
        return False
    return "src" in parts


def find_corresponding_test(source_path: Path) -> Path | None:
    tests_dir = Path.cwd() / "tests"
    if not tests_dir.exists():
        return None
    matches = list(tests_dir.rglob(f"test_{source_path.stem}.py"))
    return matches[0] if matches else None


def test_is_red(test_path: Path) -> bool:
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", str(test_path), "-q", "--no-header"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        return result.returncode != 0
    except Exception:
        return True  # fail open: cannot run pytest -> do not block


def main() -> None:
    target = resolve_target()
    if not target:
        sys.exit(0)

    source_path = Path(target)
    if not is_backend_source(source_path):
        sys.exit(0)  # only backend python under src/ is TDD-enforced

    test_path = find_corresponding_test(source_path)
    if test_path is None:
        sys.stderr.write(
            f"[TDD] BLOCKED — no test found for {source_path}.\n"
            f"      Write a failing test first (RED): "
            f"tests/test_{source_path.stem}.py\n"
        )
        sys.exit(2)

    if test_is_red(test_path):
        sys.exit(0)  # RED confirmed — proceed to GREEN

    sys.stderr.write(
        f"[TDD] note — {test_path} is currently PASSING. "
        f"Add a new failing test for new behavior; OK if refactoring.\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
