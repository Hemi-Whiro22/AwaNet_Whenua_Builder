#!/usr/bin/env python3
"""
Sync local te_po/storage content to the Supabase `tepo_storage` bucket.

This mirrors the existing storage directory structure (raw, clean, chunks, openai, logs)
into bucket paths `<stage>/<filename>`. Existing objects are overwritten (`upsert=True`).

Usage:
    python scripts/sync_storage_to_supabase.py

Requires the Supabase environment variables loaded by te_po.core.config.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from te_po.services.local_storage import DIRS
from te_po.services.supabase_uploader import upload_file
from te_po.utils.supabase_client import get_client

# Reduce noisy debug logging from Supabase/httpx during bulk uploads.
import logging

logging.getLogger().setLevel(logging.INFO)
for name in ("supabase_client", "httpx", "httpcore"):
    logging.getLogger(name).setLevel(logging.WARNING)


def sync_stage(stage: str, stage_path: Path) -> Tuple[int, int, List[Dict[str, str]]]:
    successes = 0
    failures = 0
    errors: List[Dict[str, str]] = []
    if not stage_path.exists():
        return successes, failures, errors

    for file_path in stage_path.rglob("*"):
        if not file_path.is_file():
            continue

        relative = file_path.relative_to(stage_path)
        dest_path = f"{stage}/{relative.as_posix()}"
        result = upload_file(str(file_path), dest_path)
        status = result.get("status", "unknown")
        if status == "ok":
            successes += 1
        else:
            failures += 1
            errors.append(
                {
                    "local": str(file_path),
                    "dest": dest_path,
                    "status": status,
                    "reason": result.get("reason", ""),
                }
            )
    return successes, failures, errors


def main() -> int:
    client = get_client()
    if client is None:
        print("Supabase client not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.", file=sys.stderr)
        return 1

    summary: Dict[str, Dict[str, object]] = {}
    total_success = 0
    total_fail = 0
    for stage, path in DIRS.items():
        success, fail, errors = sync_stage(stage, path)
        if success or fail:
            summary[stage] = {
                "success": success,
                "failed": fail,
                "errors": errors[:5],  # limit for readability
            }
        total_success += success
        total_fail += fail

    summary["_totals"] = {"success": total_success, "failed": total_fail}

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
