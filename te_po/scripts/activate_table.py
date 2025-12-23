"""
Utility to ensure a Supabase table is accessible.
"""

from __future__ import annotations

from te_po.core.env_loader import load_env
from te_po.services.supabase_service import get_client
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def activate_table():
    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        raise RuntimeError("Supabase client not configured.")
    try:
        response = client.table("project_state_public").select("*").limit(1).execute()
        print("Table activation successful. Response:")
        print(getattr(response, "data", None))
    except Exception as exc:
        print("Error activating table:", exc)


if __name__ == "__main__":
    activate_table()
