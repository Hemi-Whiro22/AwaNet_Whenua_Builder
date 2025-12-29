from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", "__pycache__", "node_modules", ".venv", "venv", ".gitmodules"}


def iter_entries(path: Path) -> Iterable[Path]:
    for entry in sorted(path.iterdir()):
        if entry.name in EXCLUDE:
            continue
        yield entry


def build_tree(path: Path, prefix: str = "") -> Iterable[str]:
    entries = list(iter_entries(path))
    for index, entry in enumerate(entries):
        connector = "└──" if index == len(entries) - 1 else "├──"
        yield f"{prefix}{connector} {entry.name}"
        if entry.is_dir():
            extension = "    " if index == len(entries) - 1 else "│   "
            yield from build_tree(entry, prefix + extension)


def main() -> None:
    lines = ["# Repository Tree", "", f"Base path: `{ROOT}`", ""]
    lines.append("```")
    lines.append(ROOT.name)
    lines.extend(build_tree(ROOT))
    lines.append("```")
    dest = ROOT / "analysis" / "repo_tree.md"
    dest.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
