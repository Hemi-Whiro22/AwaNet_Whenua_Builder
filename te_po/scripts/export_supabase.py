"""
Export Supabase tables to JSON files (best-effort).

Usage:
    python te_po/scripts/export_supabase.py --out te_po/storage/supabase_exports
    python te_po/scripts/export_supabase.py --tables tepo_files other_table
    python te_po/scripts/export_supabase.py --table-list extra_tables.txt
    python te_po/scripts/export_supabase.py --all
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.services.supabase_service import get_client  # noqa: E402

DEFAULT_TABLES = [
    "tepo_files",
    "tepo_pipeline_runs",
    "tepo_chunks",
    "tepo_vector_batches",
    "mauri_snapshots",
    "tepo_logs",
    "tepo_chat_logs",
]


def load_extra_tables(path: Path) -> List[str]:
    try:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception:
        return []


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
                # If schema present, keep schema-qualified names to avoid collisions
                if "table_name" in rows[0] and "schema_name" in rows[0]:
                    return sorted(
                        {f"{r.get('schema_name')}.{r.get('table_name')}" for r in rows if r.get('table_name')}
                    )
                return sorted({r.get("table_name") or r.get("tablename") for r in rows if r.get("table_name") or r.get("tablename")})
        except Exception as exc:
            print(f"[warn] table discovery via {fn} failed: {exc}")
    print("[warn] table discovery failed: no RPC helper available")
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="te_po/storage/supabase_exports", help="Output directory for JSON exports")
    parser.add_argument("--tables", nargs="*", default=None, help="Explicit tables to export")
    parser.add_argument("--table-list", type=str, default=None, help="Path to file with table names (one per line)")
    parser.add_argument("--all", action="store_true", help="Export all public tables (discovered via pg_tables)")
    parser.add_argument("--max-rows", type=int, default=10000, help="Max rows to fetch per table")
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))
    client = get_client()
    if client is None:
        print("Supabase client not configured. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
        sys.exit(1)

    tables = args.tables if args.tables else DEFAULT_TABLES
    if args.table_list:
        tables = tables + load_extra_tables(Path(args.table_list))
    if args.all:
        discovered = discover_tables(client)
        if discovered:
            tables = discovered

    # Deduplicate while keeping predictable order
    seen = set()
    uniq_tables = []
    for t in tables:
        if t and t not in seen:
            seen.add(t)
            uniq_tables.append(t)
    tables = uniq_tables

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    for table in tables:
        try:
            schema = None
            table_name = table
            if "." in table:
                schema, table_name = table.split(".", 1)
            data = []
            page_size = 1000

            # For public (or graphql_public) we can page normally
            if not schema or schema in ("public", "graphql_public"):
                table_ref = client.table(table_name) if not schema else client.schema(schema).table(table_name)
                start = 0
                while start < args.max_rows:
                    end = min(start + page_size - 1, args.max_rows - 1)
                    resp = table_ref.select("*").range(start, end).execute()
                    batch = getattr(resp, "data", None) or []
                    data.extend(batch)
                    if len(batch) < page_size:
                        break
                    start += page_size
            else:
                # For other schemas (e.g., storage, auth) attempt RPC helper
                try:
                    resp = client.rpc(
                        "select_table",
                        {"schema_name": schema, "table_name": table_name},
                    ).execute()
                    data = getattr(resp, "data", None) or []
                    if len(data) > args.max_rows:
                        data = data[: args.max_rows]
                except Exception as exc:
                    print(f"{table}: skipped (schema not accessible and RPC select_table failed: {exc})")
                    continue

            out_path = out_dir / f"{table}.json"
            out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"{table}: exported {len(data)} rows to {out_path}")
        except Exception as exc:
            print(f"{table}: export failed ({exc})")


if __name__ == "__main__":
    main()
