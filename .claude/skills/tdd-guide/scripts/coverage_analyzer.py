#!/usr/bin/env python3
"""
coverage_analyzer.py — Test quality analyzer

Detects:
  - Test functions with no assertions (vacuous tests)
  - Test functions covering only happy-path (no error/edge cases)
  - Source functions/classes with zero test coverage

Usage:
    python .claude/skills/tdd-guide/scripts/coverage_analyzer.py
    python .claude/skills/tdd-guide/scripts/coverage_analyzer.py --tests-dir tests/
    python .claude/skills/tdd-guide/scripts/coverage_analyzer.py --src-dir src/

Output: human-readable report to stdout. Exit 1 if critical issues found.
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestIssue:
    file: str
    function: str
    issue: str
    severity: str  # CRITICAL | WARNING | INFO


def collect_python_files(directory: Path) -> list[Path]:
    return list(directory.rglob("*.py"))


def find_test_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def has_assertions(func: ast.FunctionDef) -> bool:
    """Check if function contains at least one assert statement or pytest.raises."""
    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            return True
        # pytest.raises, pytest.approx, etc.
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("raises", "approx", "warns", "deprecated")
        ):
            return True
    return False


def has_error_cases(func: ast.FunctionDef) -> bool:
    """Heuristic: does the test cover error/edge cases?"""
    source = ast.unparse(func).lower()
    error_indicators = [
        "raises",
        "exception",
        "error",
        "invalid",
        "empty",
        "none",
        "zero",
        "negative",
        "overflow",
        "boundary",
        "edge",
        "fail",
        "assert.*false",
        "valueerror",
        "typeerror",
        "keyerror",
    ]
    return any(ind in source for ind in error_indicators)


def analyze_test_file(path: Path) -> list[TestIssue]:
    issues = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return [TestIssue(str(path), "N/A", f"Syntax error: {e}", "CRITICAL")]

    test_funcs = find_test_functions(tree)

    for func in test_funcs:
        if not has_assertions(func):
            issues.append(
                TestIssue(
                    file=str(path),
                    function=func.name,
                    issue="No assertions found — vacuous test (tests nothing)",
                    severity="CRITICAL",
                )
            )
        elif not has_error_cases(func):
            issues.append(
                TestIssue(
                    file=str(path),
                    function=func.name,
                    issue="Only happy-path detected — add error/edge case tests",
                    severity="WARNING",
                )
            )

    return issues


def find_untested_functions(src_dir: Path, tests_dir: Path) -> list[str]:
    """Find public functions/classes in src/ without a matching test."""
    src_names = set()
    for py_file in collect_python_files(src_dir):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith(
                "_"
            ):  # public only
                src_names.add(node.name)

    # Collect all names referenced in test files
    tested_names = set()
    for test_file in collect_python_files(tests_dir):
        try:
            source = test_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for name in src_names:
            if name in source:
                tested_names.add(name)

    return sorted(src_names - tested_names)


def main():
    parser = argparse.ArgumentParser(description="Test quality analyzer")
    parser.add_argument("--tests-dir", default="tests", help="Tests directory")
    parser.add_argument("--src-dir", default="src", help="Source directory")
    args = parser.parse_args()

    tests_dir = Path(args.tests_dir)
    src_dir = Path(args.src_dir)

    if not tests_dir.exists():
        print(f"[coverage_analyzer] Tests directory not found: {tests_dir}")
        sys.exit(0)

    print("=" * 60)
    print("TEST QUALITY REPORT")
    print("=" * 60)

    all_issues: list[TestIssue] = []
    test_files = collect_python_files(tests_dir)

    if not test_files:
        print("⚠️  No test files found.")
        sys.exit(0)

    for test_file in test_files:
        issues = analyze_test_file(test_file)
        all_issues.extend(issues)

    # Report issues
    critical = [i for i in all_issues if i.severity == "CRITICAL"]
    warnings = [i for i in all_issues if i.severity == "WARNING"]

    if critical:
        print(f"\n🔴 CRITICAL ({len(critical)} issues):")
        for issue in critical:
            print(f"  [{issue.file}] {issue.function}: {issue.issue}")

    if warnings:
        print(f"\n🟡 WARNING ({len(warnings)} issues):")
        for issue in warnings:
            print(f"  [{issue.file}] {issue.function}: {issue.issue}")

    # Untested public functions
    if src_dir.exists():
        untested = find_untested_functions(src_dir, tests_dir)
        if untested:
            print(f"\n🔵 INFO — Public names with no test reference ({len(untested)}):")
            for name in untested[:20]:  # cap at 20
                print(f"  - {name}")
            if len(untested) > 20:
                print(f"  ... and {len(untested) - 20} more")

    if not all_issues:
        print("\n✅ No test quality issues detected.")

    print("\n" + "=" * 60)

    if critical:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
