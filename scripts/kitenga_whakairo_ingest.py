#!/usr/bin/env python3
"""
Ingest selected repo documents into the carve pipeline (Supabase + OpenAI).

This helper reads Markdown/JSON/YAML/TXT files from the listed directories,
runs them through the existing pipeline orchestrator, and prints the
resulting vector batch IDs. It skips empty files and respects a
max-char limit to avoid overloading any single ingest call.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {
    ".md",
    ".markdown",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".py",
    ".rst",
    ".csv",
}
MAX_CHARS = 150_000


def find_documents(directories: Iterable[Path]) -> Iterable[Path]:
    for directory in directories:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            if any(part.startswith(".") for part in path.parts):
                continue
            yield path


def ingest_file(path: Path, mode: str) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    filename = f"whakairo_{path.relative_to(ROOT)}"
    print(f"[info] ingesting {path.relative_to(ROOT)} ({len(text)} chars)")
    result = run_pipeline(
        text.encode("utf-8"),
        filename=str(filename),
        source="kitenga_whakairo",
        mode=mode,
        metadata={"path": str(path.relative_to(ROOT)), "pipeline": "whakairo_ingest"},
        generate_summary=True,
    )
    if result.get("vector_batch_id"):
        print(f"  → batch {result['vector_batch_id']}")
    else:
        print(f"  → no batch (status={result.get('status')})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest docs via the Whakairo pipeline (Supabase + OpenAI)."
    )
    parser.add_argument(
        "--mode",
        choices=["research", "taonga"],
        default="research",
        help="Mode for the carving pipeline.",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=["analysis", "docs", "te_hau"],
        help="Directories relative to the repo root to ingest.",
    )
    args = parser.parse_args()

    directories = [ROOT / Path(dirpath) for dirpath in args.dirs]
    for path in find_documents(directories):
        try:
            ingest_file(path, args.mode)
        except Exception as exc:
            print(f"[error] failed to ingest {path.relative_to(ROOT)}: {exc}")


if __name__ == "__main__":
    main()
