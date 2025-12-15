"""
Lightweight Supabase client helpers with safe fallbacks.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None  # type: ignore

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("DEN_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("DEN_API_KEY")

supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None


def get_client():
    return supabase


def _apply_filters(query, filters: Optional[Dict[str, Any]] = None):
    if not filters:
        return query
    for key, value in filters.items():
        query = query.eq(key, value)
    return query


def insert_record(table: str, record: Dict[str, Any], upsert: bool = False):
    if supabase is None:
        return {"data": None, "error": "supabase client not configured"}
    try:
        q = supabase.table(table)
        return (q.upsert(record) if upsert else q.insert(record)).execute()
    except Exception as exc:
        return {"data": None, "error": str(exc)}


def fetch_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    order_by: Optional[str] = None,
    desc: bool = True,
):
    if supabase is None:
        return {"data": None, "error": "supabase client not configured"}
    try:
        q = supabase.table(table).select("*")
        q = _apply_filters(q, filters)
        if order_by:
            q = q.order(order_by, desc=desc)
        q = q.limit(limit)
        return q.execute()
    except Exception as exc:
        return {"data": None, "error": str(exc)}


def fetch_latest(table: str, order_by: str = "created_at"):
    return fetch_records(table, limit=1, order_by=order_by, desc=True)


def update_record(table: str, filters: Dict[str, Any], values: Dict[str, Any]):
    if supabase is None:
        return {"data": None, "error": "supabase client not configured"}
    try:
        q = supabase.table(table).update(values)
        q = _apply_filters(q, filters)
        return q.execute()
    except Exception as exc:
        return {"data": None, "error": str(exc)}


def delete_record(table: str, filters: Dict[str, Any]):
    if supabase is None:
        return {"data": None, "error": "supabase client not configured"}
    try:
        q = supabase.table(table).delete()
        q = _apply_filters(q, filters)
        return q.execute()
    except Exception as exc:
        return {"data": None, "error": str(exc)}


__all__ = [
    "supabase",
    "get_client",
    "insert_record",
    "fetch_records",
    "fetch_latest",
    "update_record",
    "delete_record",
]
