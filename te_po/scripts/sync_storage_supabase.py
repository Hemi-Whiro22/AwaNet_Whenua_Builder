"""
Sync Te Pō local storage metadata to Supabase (dry-run by default).

What it does:
- Scans te_po/storage/{raw,clean,chunks,openai}
- Optionally uploads files to a Supabase storage bucket
- Optionally upserts metadata rows to a Supabase table

Env required for live mode:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY (or ANON_KEY for testing)

Usage:
    python te_po/scripts/sync_storage_supabase.py          # dry-run only
    python te_po/scripts/sync_storage_supabase.py --live   # attempt uploads/inserts
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import hashlib
from mimetypes import guess_type
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.services.supabase_service import get_client, upload_file, insert_record

ROOT = Path(__file__).resolve().parents[2]
STORAGE_ROOT = ROOT / "te_po" / "storage"

BUCKET_NAME = os.getenv("SUPABASE_BUCKET_STORAGE") or "tepo_storage"
TABLE_NAME = os.getenv("SUPABASE_TABLE_FILES") or "tepo_files"


def scan_files() -> list[dict]:
    buckets = ["raw", "clean", "chunks", "openai"]
    entries: list[dict] = []
    for bucket in buckets:
        folder = STORAGE_ROOT / bucket
        if not folder.exists():
            continue
        for f in folder.iterdir():
            if not f.is_file():
                continue
            entries.append(
                {
                    "bucket": bucket,
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                }
            )
    return entries


def dry_run(entries: list[dict]):
    print(f"[dry-run] found {len(entries)} files")
    for e in entries[:10]:
        print(f"  - {e['bucket']}/{e['name']} ({e['size']} bytes)")
    if len(entries) > 10:
        print(f"  ... and {len(entries) - 10} more")


def ensure_bucket(client, bucket: str):
    try:
        # Try to create; if it already exists, ignore the error.
        client.storage.create_bucket(bucket)
        print(f"[live] created bucket {bucket}")
    except Exception as exc:
        # If duplicate, it's fine; otherwise warn.
        if "Bucket already exists" in str(exc) or "Duplicate" in str(exc):
            return
        print(f"[warn] bucket create failed: {exc}")


def upload_and_record(client, entries: list[dict], live: bool):
    ensure_bucket(client, BUCKET_NAME)
    uploaded = 0
    for e in entries:
        rel_path = f"{e['bucket']}/{e['name']}"
        try:
            if live:
                upload_res = upload_file(e["path"], rel_path)
                if upload_res.get("status") != "ok":
                    print(f"[warn] upload failed {rel_path}: {upload_res.get('reason')}")
                insert_record(
                    TABLE_NAME,
                    {
                        "storage_bucket": BUCKET_NAME,
                        "storage_path": rel_path,
                        "filename": e["name"],
                        "size": e["size"],
                        "content_type": guess_type(e["name"])[0],
                        "sha256": hashlib.sha256(Path(e["path"]).read_bytes()).hexdigest(),
                    },
                    upsert=True,
                )
        except Exception as exc:
            print(f"[warn] upload failed {rel_path}: {exc}")
        uploaded += 1
    print(f"[live] processed {uploaded} files (uploads may be duplicates; metadata upserts attempted)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live", action="store_true", help="Perform actual uploads and inserts"
    )
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()

    entries = scan_files()
    if not args.live:
        dry_run(entries)
        return

    if client is None:
        print("Supabase client not configured; aborting live sync.")
        return

    upload_and_record(client, entries, live=True)


if __name__ == "__main__":
    main()
