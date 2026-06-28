from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Source areas where architecture/doc style should be enforced.
SOURCE_GLOBS = [
    PROJECT_ROOT / "main.py",
    PROJECT_ROOT / "config.py",
    PROJECT_ROOT / "engine",
    PROJECT_ROOT / "models",
    PROJECT_ROOT / "versioning",
]


def _iter_python_files() -> list[Path]:
    files: list[Path] = []

    for entry in SOURCE_GLOBS:
        if entry.is_file() and entry.suffix == ".py":
            files.append(entry)
            continue

        if entry.is_dir():
            files.extend(path for path in entry.rglob("*.py") if path.name != "__init__.py")

    return sorted(set(files))


def _has_required_sections(docstring: str) -> bool:
    return "Args:" in docstring and "Returns:" in docstring


def _format_location(path: Path, line_number: int, symbol: str) -> str:
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    return f"{rel}:{line_number} -> {symbol}"


def test_stylecop_docstrings_for_classes_and_methods() -> None:
    """Fail when classes/methods/functions do not follow project docstring contract.

    Args:
        None.

    Returns:
        None.
    """
    missing: list[str] = []

    for file_path in _iter_python_files():
        module = ast.parse(file_path.read_text(encoding="utf-8"))

        for node in module.body:
            if isinstance(node, ast.ClassDef):
                class_doc = ast.get_docstring(node)
                if not class_doc or not _has_required_sections(class_doc):
                    missing.append(_format_location(file_path, node.lineno, f"class {node.name}"))

                for member in node.body:
                    if isinstance(member, ast.FunctionDef):
                        member_doc = ast.get_docstring(member)
                        if not member_doc or not _has_required_sections(member_doc):
                            missing.append(
                                _format_location(
                                    file_path,
                                    member.lineno,
                                    f"{node.name}.{member.name}",
                                )
                            )

            elif isinstance(node, ast.FunctionDef):
                fn_doc = ast.get_docstring(node)
                if not fn_doc or not _has_required_sections(fn_doc):
                    missing.append(_format_location(file_path, node.lineno, f"function {node.name}"))

    assert not missing, "DocStyle violations:\n" + "\n".join(missing)
