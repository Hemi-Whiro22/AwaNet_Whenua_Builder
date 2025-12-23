"""
Snapshot Supabase public tables and row counts into Mauri state JSON.

Usage:
    python te_po/scripts/snapshot_supabase_tables.py
    python te_po/scripts/snapshot_supabase_tables.py --out mauri/state/supabase_tables.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.services.supabase_service import get_client  # noqa: E402

DEFAULT_OUT = ROOT / "mauri" / "state" / "supabase_tables.json"


def discover_tables(client) -> List[str]:
    """
    Discover tables via RPC helper. Tries `list_tables_ext`, then `list_tables_all`, then `list_public_tables`.
    """
    for fn in ("list_tables_ext", "list_tables_all", "list_public_tables"):
        try:
            resp = client.rpc(fn).execute()
            rows = getattr(resp, "data", None) or []
            if rows and isinstance(rows[0], str):
                return sorted(rows)
            if rows and isinstance(rows[0], dict):
                if "table_name" in rows[0] and "schema_name" in rows[0]:
                    return sorted(
                        {f"{r.get('schema_name')}.{r.get('table_name')}" for r in rows if r.get('table_name')}
                    )
                return sorted({r.get("table_name") or r.get("tablename") for r in rows if r.get("table_name") or r.get("tablename")})
        except Exception as exc:
            print(f"[warn] table discovery via {fn} failed: {exc}")
    print("[warn] table discovery failed: no RPC helper available")
    return []


def count_rows(client, table: str):
    try:
        schema = None
        table_name = table
        if "." in table:
            schema, table_name = table.split(".", 1)
        if schema and schema not in ("public", "graphql_public"):
            # Try RPC helper for non-public schemas
            try:
                resp = client.rpc(
                    "select_table",
                    {"schema_name": schema, "table_name": table_name},
                ).execute()
                data = getattr(resp, "data", None) or []
                return len(data)
            except Exception as exc:
                return f"skipped (schema not accessible and RPC select_table failed: {exc})"
        table_ref = client.table(table_name) if not schema else client.schema(schema).table(table_name)
        resp = table_ref.select("count", count="exact").limit(1).execute()
        return getattr(resp, "count", None)
    except Exception as exc:
        return f"error: {exc}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Path to write the snapshot JSON (default mauri/state/supabase_tables.json)",
    )
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        sys.exit(1)

    tables = discover_tables(client)
    if not tables:
        print("No tables discovered; aborting snapshot.")
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    for table in tables:
        rows = count_rows(client, table)
        results.append({"table": table, "rows": rows})
        print(f"{table}: {rows}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "public",
        "tables": results,
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Snapshot written to {args.out}")


if __name__ == "__main__":
    main()
