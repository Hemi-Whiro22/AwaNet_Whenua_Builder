#!/usr/bin/env python3
"""
run_kaitiaki_meta_trace — keep the mauri in our metadata tags.

Scans the repo for meta tags, placeholder names, and suspicious ownership labels.
Creates a human-friendly report showing any files that may leak external branding
or drop the `AwaNet Kaitiaki Collective` signature.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPORT_PATH = Path(__file__).resolve().parent / "kaitiaki_meta_trace_report.txt"
ROOT = Path(__file__).resolve().parents[1]
OUR_OWNERSHIP_LABEL = "AwaNet Kaitiaki Collective"

OUR_NAMES = [
    "Kitenga",
    "Kaitiaki",
    "AwaNet",
    "Te Hau",
    "Te Pō",
    "Te Ao",
    "Tiwhanawhana",
    "Whaimārama",
    "Koru Wolf",
]

PLACEHOLDER_PATTERNS = [
    r"company name",
    r"project name",
    r"Your Brand",
    r"Lorem Ipsum",
    r"(?<!AwaNet\s)Kaitiaki Collective",
    r"your startup",
    r"foo bar",
    r"example\.com",
]

SUSPICIOUS_OWNERS = [
    "Kaitiaki Collective",
    "Mauri Systems",
    "Kaitiaki Labs",
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
TEXT_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".json", ".yaml", ".yml", ".html", ".htm"}


def scan_file(path: Path) -> List[str]:
    issues: List[str] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return [f"Unable to read file: {exc}"]

    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Placeholder pattern matched: '{pattern}'")

    ownership_matches = re.findall(r"\"ownership\"\\s*:\\s*\"([^\"]+)\"", content)
    for found in ownership_matches:
        if found != OUR_OWNERSHIP_LABEL:
            issues.append(f"Ownership tag differs from ours: '{found}'")

    for suspicious in SUSPICIOUS_OWNERS:
        for match in re.finditer(re.escape(suspicious), content, re.IGNORECASE):
            if match.group(0).lower() == OUR_OWNERSHIP_LABEL.lower():
                continue
            start = max(0, match.start() - 20)
            snippet = content[start:match.start()]
            if "AwaNet" in snippet:
                continue
            issues.append(f"Suspicious external name found: '{suspicious}'")

    return issues


def walk_repo(root: Path) -> Dict[Path, List[str]]:
    flagged: Dict[Path, List[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            results = scan_file(path)
            if results:
                flagged[path] = results
    return flagged


def write_report(flagged: Dict[Path, List[str]], report_path: Path) -> None:
    lines: List[str] = []
    if not flagged:
        lines.append("No meta concerns detected.")
    else:
        lines.append("Kaitiaki meta trace results:")
        lines.append("")
        for path in sorted(flagged):
            lines.append(f"{path.relative_to(ROOT)}:")
            for issue in flagged[path]:
                lines.append(f"  - {issue}")
            lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trace meta tags and placeholder names.")
    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=ROOT,
        help="Root path to scan (defaults to repository root).",
    )
    parser.add_argument(
        "--report",
        "-o",
        type=Path,
        default=REPORT_PATH,
        help="Report file path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    flagged = walk_repo(args.root)
    write_report(flagged, args.report)
    print(f"Meta trace complete. Report saved to {args.report}")
    if flagged:
        print(f"{len(flagged)} files flagged. Review {args.report}")


if __name__ == "__main__":
    main()
