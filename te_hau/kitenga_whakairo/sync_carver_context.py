"""
Sync carver context/memory from Supabase into local mauri/state anchors.

Pulls:
- carver_context_memory (recent rows)
- kitenga.logs (optional, recent rows)

Writes:
- mauri/state/carver_context_cache.json

Usage:
    python te_hau/whakairo/sync_carver_context.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

# Repo root (/workspaces/The_Awa_Network)
ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "mauri" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

import sys

sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.utils.supabase_client import get_client  # noqa: E402


def fetch_table(client, table: str, limit: int = 50):
    try:
        resp = client.table(table).select("*").order("created_at", desc=True).limit(limit).execute()
        return getattr(resp, "data", None) or []
    except Exception as exc:
        return {"error": str(exc)}


def main():
    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured; aborting.")
        return

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "carver_context_memory": fetch_table(client, "carver_context_memory", limit=100),
        "kitenga_logs": fetch_table(client, "kitenga_logs", limit=200),
    }

    out_path = STATE_DIR / "carver_context_cache.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
