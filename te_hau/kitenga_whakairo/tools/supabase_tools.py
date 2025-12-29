import os
import re
from typing import Any, Dict, Optional

from te_po.utils.supabase_client import get_client, fetch_records

DESTRUCTIVE_SQL = re.compile(r"\b(drop|truncate|delete|alter|update|insert)\b", re.IGNORECASE)
SQL_FN = os.getenv("SUPABASE_SQL_FN", "execute_sql")


def _client():
    return get_client()


def supabase_table_select(ctx: Any, table: str, limit: int = 50, order_by: Optional[str] = None, desc: bool = True):
    """Fetch rows from a table with optional ordering."""
    resp = fetch_records(table, limit=limit, order_by=order_by, desc=desc)
    if isinstance(resp, dict) and resp.get("error"):
        return {"error": resp["error"]}
    return getattr(resp, "data", None) or getattr(resp, "model", None) or []


def supabase_search(ctx: Any, table: str, query: str, limit: int = 20):
    client = _client()
    if client is None:
        return {"error": "Supabase client not configured."}
    try:
        result = client.table(table).select("*").ilike("content", f"%{query}%").limit(limit).execute()
        return getattr(result, "data", None)
    except Exception as exc:
        return {"error": str(exc)}


def supabase_insert(ctx: Any, table: str, record: Dict[str, Any], upsert: bool = False):
    client = _client()
    if client is None:
        return {"error": "Supabase client not configured."}
    try:
        q = client.table(table)
        result = (q.upsert(record) if upsert else q.insert(record)).execute()
        return getattr(result, "data", None)
    except Exception as exc:
        return {"error": str(exc)}


def supabase_storage_list(ctx: Any, bucket: str, path: str = "", limit: int = 100):
    client = _client()
    if client is None:
        return {"error": "Supabase client not configured."}
    try:
        storage = client.storage.from_(bucket)
        return storage.list(path=path or "", limit=limit)
    except Exception as exc:
        return {"error": str(exc)}


def supabase_sql(ctx: Any, sql: str, allow_write: bool = False, fn: Optional[str] = None):
    """
    Execute SQL through a Postgres function (default: execute_sql).
    Blocks destructive commands unless allow_write=True.
    """
    client = _client()
    if client is None:
        return {"error": "Supabase client not configured."}

    if not allow_write and DESTRUCTIVE_SQL.search(sql):
        return {"error": "Destructive SQL blocked; set allow_write=True to override."}

    try:
        func_name = fn or SQL_FN
        result = client.rpc(func_name, {"sql": sql}).execute()
        return getattr(result, "data", None)
    except Exception as exc:
        return {"error": str(exc)}
