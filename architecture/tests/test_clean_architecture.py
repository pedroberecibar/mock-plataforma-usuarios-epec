"""
Architecture fitness functions — Clean Architecture layer rules (Python)

These tests enforce that the dependency direction is always:
  Interface → Application → Domain
  Infrastructure → Application → Domain

Domain must NEVER import from Application, Infrastructure, or Interface.
Application must NEVER import from Infrastructure or Interface.

Run with: pytest architecture/tests/ -v
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent.parent / "src"

# Allowed import prefixes per layer
LAYER_RULES: dict[str, list[str]] = {
    "domain": ["domain"],
    "application": ["application", "domain"],
    "infrastructure": ["infrastructure", "application", "domain"],
    "interface": ["interface", "application", "domain"],
}


def collect_imports(py_file: Path) -> list[str]:
    """Extract all top-level module imports from a Python file."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def get_layer(py_file: Path) -> str | None:
    """Determine which layer a file belongs to based on its path."""
    rel = py_file.relative_to(SRC)
    parts = rel.parts
    if not parts:
        return None
    top = parts[0].lower()
    return top if top in LAYER_RULES else None


def is_internal_import(module: str) -> bool:
    """Return True if the import references internal project code (src/)."""
    # Internal if starts with a known layer name
    return any(module.startswith(layer) for layer in LAYER_RULES)


def collect_layer_files() -> list[tuple[Path, str]]:
    """Return (file, layer) pairs for all Python files under src/."""
    if not SRC.exists():
        return []
    result = []
    for py_file in SRC.rglob("*.py"):
        layer = get_layer(py_file)
        if layer:
            result.append((py_file, layer))
    return result


@pytest.mark.parametrize("py_file,layer", collect_layer_files())
def test_layer_dependencies(py_file: Path, layer: str) -> None:
    """Each file must only import from layers allowed for its layer."""
    allowed_prefixes = LAYER_RULES[layer]
    imports = collect_imports(py_file)

    violations = []
    for module in imports:
        if not is_internal_import(module):
            continue  # stdlib or third-party — skip
        allowed = any(module.startswith(prefix) for prefix in allowed_prefixes)
        if not allowed:
            violations.append(module)

    assert not violations, (
        f"Layer '{layer}' violation in {py_file.relative_to(SRC.parent)}:\n"
        f"  Forbidden imports: {violations}\n"
        f"  Allowed layers: {allowed_prefixes}"
    )


def test_domain_has_no_infrastructure_imports() -> None:
    """Domain layer must be pure — zero infrastructure imports."""
    if not SRC.exists():
        pytest.skip("src/ directory not found")

    domain_dir = SRC / "domain"
    if not domain_dir.exists():
        pytest.skip("src/domain/ directory not found")

    forbidden = ["infrastructure", "interface"]
    violations = []

    for py_file in domain_dir.rglob("*.py"):
        for module in collect_imports(py_file):
            if any(module.startswith(f) for f in forbidden):
                violations.append(f"{py_file.name}: imports {module}")

    assert not violations, (
        "Domain layer MUST NOT import infrastructure or interface:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )
