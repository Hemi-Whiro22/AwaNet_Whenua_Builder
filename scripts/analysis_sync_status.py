#!/usr/bin/env python3
"""
CLI to report the latest analysis sync status stored in Supabase.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from analysis.sync_status import (
    fetch_analysis_sync_status,
    fetch_latest_analysis_document_content,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Report Supabase analysis sync status")
    parser.add_argument(
        "--document",
        action="store_true",
        help="Return the latest analysis document payload stored in Supabase",
    )
    args = parser.parse_args()
    if args.document:
        doc = fetch_latest_analysis_document_content()
        print(json.dumps(doc, indent=2, ensure_ascii=False))
    else:
        status = fetch_analysis_sync_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
