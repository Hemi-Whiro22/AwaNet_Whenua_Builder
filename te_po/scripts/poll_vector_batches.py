"""
Poll OpenAI vector batch statuses and update Supabase (tepo_vector_batches).

Usage:
    python te_po/scripts/poll_vector_batches.py          # one-shot
    python te_po/scripts/poll_vector_batches.py --watch  # loop every 30s
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.services.supabase_service import get_client  # noqa: E402
from te_po.utils.openai_client import client as oa_client  # noqa: E402
from te_po.utils.audit import log_event  # noqa: E402

FINAL = {"completed", "failed", "cancelled", "expired"}


def fetch_batches(client):
    try:
        resp = client.table("tepo_vector_batches").select("*").limit(500).execute()
        return getattr(resp, "data", None) or []
    except Exception as exc:
        print(f"[warn] fetch failed: {exc}")
        return []


def update_batch(client, batch_id: str, status: str, metadata):
    try:
        client.table("tepo_vector_batches").update(
            {"status": status, "metadata": metadata or {}, "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        ).eq("batch_id", batch_id).execute()
    except Exception as exc:
        print(f"[warn] update failed for {batch_id}: {exc}")


def poll_once():
    client = get_client()
    if client is None or oa_client is None:
        print("Supabase or OpenAI client not configured; aborting.")
        return

    batches = fetch_batches(client)
    if not batches:
        print("No batches found.")
        return

    for row in batches:
        batch_id = row.get("batch_id")
        status = (row.get("status") or "").lower()
        vector_store_id = row.get("vector_store_id") or None
        if not batch_id or not vector_store_id:
            continue
        if status in FINAL:
            continue
        try:
            resp = oa_client.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store_id,
                file_batch_id=batch_id,
            )
            new_status = getattr(resp, "status", None)
            payload = (
                resp.model_dump()
                if hasattr(resp, "model_dump")
                else resp.to_dict_recursive()
                if hasattr(resp, "to_dict_recursive")
                else None
            )
            update_batch(client, batch_id, new_status, payload)
            log_event(
                "vector_batch_status",
                f"Batch {batch_id} status -> {new_status}",
                source="vector_batch_poller",
                data={"vector_store_id": vector_store_id, "batch": payload},
            )
            print(f"{batch_id}: {status} -> {new_status}")
        except Exception as exc:
            print(f"[warn] poll failed for {batch_id}: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Poll every 30 seconds")
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))

    if not args.watch:
        poll_once()
        return

    while True:
        poll_once()
        time.sleep(30)


if __name__ == "__main__":
    main()
