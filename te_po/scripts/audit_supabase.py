"""
Audit Supabase tables for Te Pō. Checks existence and row counts for expected tables.

Usage:
    python te_po/scripts/audit_supabase.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.utils.supabase_client import get_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_TABLES = [
    "tepo_files",
    "tepo_pipeline_runs",
    "tepo_chunks",
    "tepo_vector_batches",
    "mauri_snapshots",
    "tepo_logs",
    "tepo_chat_logs",
]


def main():
    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        sys.exit(1)

    for table in EXPECTED_TABLES:
        try:
            resp = client.table(table).select("count", count="exact").limit(1).execute()
            count = getattr(resp, "count", None)
            print(f"{table}: ok, rows={count}")
        except Exception as exc:
            print(f"{table}: missing or inaccessible ({exc})")


if __name__ == "__main__":
    main()
