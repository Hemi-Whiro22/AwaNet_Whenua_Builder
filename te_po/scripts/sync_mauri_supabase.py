"""
Sync key Mauri/state files to Supabase (dry-run by default).

Targets:
- Files: mauri/global_env.json, mauri/state/*.json, mauri/context.md,
         te_po/openai_tools.json, te_po/openai_assistants.json
- Bucket: SUPABASE_BUCKET_MAURI (default: mauri_state)
- Table: SUPABASE_TABLE_MAURI (default: mauri_snapshots)

Usage:
    python te_po/scripts/sync_mauri_supabase.py          # dry-run only
    python te_po/scripts/sync_mauri_supabase.py --live   # upload + upsert metadata
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from te_po.core.env_loader import load_env
from te_po.utils.supabase_client import get_client

ROOT = Path(__file__).resolve().parents[2]


def collect_targets() -> List[Path]:
    targets = [
        ROOT / "mauri" / "global_env.json",
        ROOT / "mauri" / "context.md",
        ROOT / "te_po" / "openai_tools.json",
        ROOT / "te_po" / "openai_assistants.json",
    ]
    targets += list((ROOT / "mauri" / "state").glob("*.json"))
    return [p for p in targets if p.exists()]


def dry_run(files: List[Path]):
    print(f"[dry-run] found {len(files)} Mauri/state files to sync")
    for p in files:
        print(f"  - {p.relative_to(ROOT)} ({p.stat().st_size} bytes)")


def sync(files: List[Path], live: bool):
    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if not live:
        dry_run(files)
        return
    if client is None:
        print("Supabase client not configured; aborting live sync.")
        return

    bucket = os.getenv("SUPABASE_BUCKET_MAURI", "mauri_state")
    table = os.getenv("SUPABASE_TABLE_MAURI", "mauri_snapshots")
    ts = datetime.now(timezone.utc).isoformat()

    uploaded = []
    for p in files:
        rel = str(p.relative_to(ROOT))
        dest = rel
        try:
            with open(p, "rb") as fh:
                client.storage.from_(bucket).upload(dest, fh)
            uploaded.append({"path": dest, "size": p.stat().st_size})
        except Exception as exc:
            print(f"[warn] upload failed {dest}: {exc}")

    try:
        if uploaded:
            client.table(table).upsert(
                {
                    "snapshot_ts": ts,
                    "files": uploaded,
                    "count": len(uploaded),
                }
            ).execute()
            print(f"[live] recorded snapshot in {table}")
    except Exception as exc:
        print(f"[warn] snapshot upsert failed: {exc}")

    print(f"[live] uploaded {len(uploaded)} files to bucket {bucket}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Perform uploads and snapshot insert")
    args = parser.parse_args()
    files = collect_targets()
    sync(files, live=args.live)


if __name__ == "__main__":
    main()
