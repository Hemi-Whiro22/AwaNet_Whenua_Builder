"""
Clear Supabase tables for Te Pō (default dry-run).

Usage:
    python te_po/scripts/clear_supabase_tables.py           # dry-run
    python te_po/scripts/clear_supabase_tables.py --live    # delete rows
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.services.supabase_service import get_client  # noqa: E402

TABLES = [
    "tepo_files",
    "tepo_pipeline_runs",
    "tepo_chunks",
    "tepo_vector_batches",
    "mauri_snapshots",
    "tepo_logs",
    "tepo_chat_logs",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Actually delete rows")
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        sys.exit(1)

    for table in TABLES:
        if not args.live:
            print(f"[dry-run] would delete all rows from {table}")
            continue
        try:
            resp = client.table(table).delete().neq("id", None).execute()
            count = len(getattr(resp, "data", []) or [])
            print(f"{table}: deleted {count} rows")
        except Exception as exc:
            print(f"{table}: delete failed ({exc})")


if __name__ == "__main__":
    main()
