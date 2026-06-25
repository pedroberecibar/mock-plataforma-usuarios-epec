"""Tests for scripts/capture_decision.py (refined: explicit marker, command-only).

The script lives in scripts/ (not on pythonpath), so we load it by file path.
"""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "capture_decision.py"
_spec = importlib.util.spec_from_file_location("capture_decision", _SCRIPT)
assert _spec and _spec.loader
capture_decision = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capture_decision)


class TestExtractDecision:
    def test_marker_returns_text_after_it(self) -> None:
        assert capture_decision.extract_decision("@decision Elegimos SQLite") == "Elegimos SQLite"

    def test_marker_is_case_insensitive(self) -> None:
        assert capture_decision.extract_decision("@DECISION Usar hexagonal") == "Usar hexagonal"

    def test_adr_marker_is_supported(self) -> None:
        assert (
            capture_decision.extract_decision("@adr Migramos a Postgres") == "Migramos a Postgres"
        )

    def test_marker_inside_echo_strips_quotes_and_trailing_command(self) -> None:
        cmd = 'echo "@decision Elegimos X sobre Y" && ls'
        assert capture_decision.extract_decision(cmd) == "Elegimos X sobre Y"

    def test_optional_separator_after_marker(self) -> None:
        assert capture_decision.extract_decision("@decision: Hola") == "Hola"

    def test_plain_inspection_command_returns_none(self) -> None:
        assert capture_decision.extract_decision("git status") is None

    def test_keyword_without_marker_returns_none(self) -> None:
        # The old broad heuristic must no longer trigger.
        assert capture_decision.extract_decision('echo "decidimos algo de arquitectura"') is None

    def test_empty_marker_returns_none(self) -> None:
        assert capture_decision.extract_decision("@decision   ") is None


class TestReadHookCommand:
    def test_returns_command_field(self) -> None:
        raw = '{"tool_input": {"command": "ls -la"}, "tool_response": {"stdout": "x"}}'
        assert capture_decision.read_hook_command(raw) == "ls -la"

    def test_ignores_tool_output_entirely(self) -> None:
        # A decision marker in the OUTPUT must not be picked up: only the command counts.
        raw = '{"tool_input": {"command": "cat note.md"}, "tool_response": {"stdout": "@decision foo"}}'
        command = capture_decision.read_hook_command(raw)
        assert capture_decision.extract_decision(command) is None

    def test_malformed_json_returns_empty(self) -> None:
        assert capture_decision.read_hook_command("not json") == ""


class TestAppendDecision:
    def test_writes_clean_text_not_raw_dump(self, tmp_path: Path) -> None:
        capture_decision.append_decision(tmp_path, "demo", "Elegimos SQLite por el MVP")
        note = (
            tmp_path
            / "Projects"
            / "demo"
            / f"{capture_decision.date.today().isoformat()}-session.md"
        )
        content = note.read_text(encoding="utf-8")
        assert "Elegimos SQLite por el MVP" in content
        # Must not wrap the entry in a raw code block dump of command+output.
        assert "```" not in content

    def test_appends_without_overwriting(self, tmp_path: Path) -> None:
        capture_decision.append_decision(tmp_path, "demo", "Primera")
        capture_decision.append_decision(tmp_path, "demo", "Segunda")
        note = (
            tmp_path
            / "Projects"
            / "demo"
            / f"{capture_decision.date.today().isoformat()}-session.md"
        )
        content = note.read_text(encoding="utf-8")
        assert "Primera" in content and "Segunda" in content
