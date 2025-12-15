"""
Compare Supabase storage objects vs tepo_files metadata and report drift.

Usage:
    python te_po/scripts/storage_drift_check.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.utils.supabase_client import get_client  # noqa: E402


def fetch_tepo_files(client):
    resp = client.table("tepo_files").select("storage_bucket,storage_path,sha256,size").limit(2000).execute()
    return getattr(resp, "data", None) or []


def fetch_storage_objects(client):
    resp = client.schema("storage").table("objects").select("bucket_id,name,metadata").limit(5000).execute()
    return getattr(resp, "data", None) or []


def compare(files, objects):
    files_map = {(f.get("storage_bucket") or "", f.get("storage_path") or ""): f for f in files}
    objects_map = defaultdict(list)
    for o in objects:
        objects_map[(o.get("bucket_id") or "", o.get("name") or "")].append(o)

    missing_in_objects = []
    missing_in_files = []
    hash_mismatch = []

    for key, f in files_map.items():
        bucket, path = key
        obj_list = objects_map.get(key)
        if not obj_list:
            missing_in_objects.append(key)
            continue
        # If hashes are present, compare
        file_hash = f.get("sha256")
        if file_hash and obj_list:
            obj_hash = obj_list[0].get("metadata", {}).get("eTag") or None
            # eTag is not sha256; we can't reliably compare, so skip hash check here.

    for key, objs in objects_map.items():
        if key not in files_map:
            missing_in_files.append(key)

    return missing_in_objects, missing_in_files, hash_mismatch


def main():
    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured.")
        return

    files = fetch_tepo_files(client)
    objects = fetch_storage_objects(client)

    missing_in_objects, missing_in_files, hash_mismatch = compare(files, objects)

    print(f"tepo_files rows: {len(files)}, storage.objects rows: {len(objects)}")
    print(f"Missing in storage.objects (present in tepo_files): {len(missing_in_objects)}")
    if missing_in_objects:
        for item in missing_in_objects[:20]:
            print(f"  - {item}")
        if len(missing_in_objects) > 20:
            print(f"  ... and {len(missing_in_objects) - 20} more")

    print(f"Missing in tepo_files (present in storage.objects): {len(missing_in_files)}")
    if missing_in_files:
        for item in missing_in_files[:20]:
            print(f"  - {item}")
        if len(missing_in_files) > 20:
            print(f"  ... and {len(missing_in_files) - 20} more")

    if hash_mismatch:
        print(f"Hash mismatches: {len(hash_mismatch)}")
    else:
        print("Hash mismatches: not checked (eTag not comparable to sha256).")


if __name__ == "__main__":
    main()
