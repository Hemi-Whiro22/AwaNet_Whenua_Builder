"""Generate a catalog of markdown files across the repo."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
EXCLUDES = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", ".pytest_cache"}


def iter_markdown_files() -> Iterable[Path]:
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in EXCLUDES for part in path.parts):
            continue
        yield path


def extract_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip()
    return "(no heading)"


def build_rows() -> list[tuple[str, str, int]]:
    rows = []
    for path in iter_markdown_files():
        rows.append((str(path.relative_to(ROOT)), extract_heading(path), path.stat().st_size))
    return rows


def render_table(rows: list[tuple[str, str, int]]) -> str:
    lines = ["| Path | Title | Size (bytes) |", "| --- | --- | --- |"]
    for path, title, size in rows:
        lines.append(f"| `{path}` | {title or '—'} | {size} |")
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    target = ROOT / "docs" / "markdown_catalog.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    content = (
        "# Markdown Catalog\n\n"
        f"_Generated on {now.isoformat()} UTC._\n\n"
        f"Total files: {len(rows)}\n\n"
        f"{render_table(rows)}\n"
    )
    target.write_text(content, encoding="utf-8")
    print(f"Generated catalog at {target}")


if __name__ == "__main__":
    main()
