from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]

INCLUDE_EXTENSIONS = {
    ".py": "Python",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
}

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".streamlit",
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except UnicodeDecodeError:
        return 0


def count_python_objects(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0, 0

    classes = 0
    functions = 0
    dataclasses = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes += 1

            for decorator in node.decorator_list:
                if getattr(decorator, "id", "") == "dataclass":
                    dataclasses += 1
                elif getattr(decorator, "attr", "") == "dataclass":
                    dataclasses += 1

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1

    return classes, functions, dataclasses


def read_version() -> str:
    version_file = ROOT / "VERSION"

    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()

    return "unknown"


def main():
    file_counts = {}
    line_counts = {}

    total_classes = 0
    total_functions = 0
    total_dataclasses = 0

    for path in ROOT.rglob("*"):
        if should_ignore(path) or not path.is_file():
            continue

        label = INCLUDE_EXTENSIONS.get(path.suffix)

        if not label:
            continue

        file_counts[label] = file_counts.get(label, 0) + 1
        line_counts[label] = line_counts.get(label, 0) + count_lines(path)

        if path.suffix == ".py":
            classes, functions, dataclasses = count_python_objects(path)
            total_classes += classes
            total_functions += functions
            total_dataclasses += dataclasses

    print("=" * 48)
    print("        GRIDIRON CORTEX PROJECT STATS")
    print("=" * 48)
    print(f"Project Version       {read_version()}")
    print()

    for label in sorted(file_counts):
        print(f"{label + ' Files':<22}{file_counts[label]:>8}")
        print(f"{label + ' LOC':<22}{line_counts[label]:>8}")

    print()
    print(f"{'Classes':<22}{total_classes:>8}")
    print(f"{'Dataclasses':<22}{total_dataclasses:>8}")
    print(f"{'Functions':<22}{total_functions:>8}")
    print("=" * 48)


if __name__ == "__main__":
    main()
