"""
Lightweight Supabase client helpers with safe fallbacks.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from functools import lru_cache
import logging
from te_po.core.config import settings

try:
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None  # type: ignore

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("supabase_client")

# Debugging Supabase client initialization
logger.debug(f"SUPABASE_URL: {settings.supabase_url}")
logger.debug(f"SUPABASE_KEY: {'Provided' if settings.supabase_service_role_key else 'Not Provided'}")

supabase = None
if create_client and settings.supabase_url and settings.supabase_service_role_key:
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        logger.debug("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None
else:
    logger.warning("Supabase client not initialized. Missing URL or Key.")


def get_client():
    if supabase is None:
        logger.error("Supabase client is not configured.")
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


@lru_cache(maxsize=128)
def cached_fetch_records(table: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100, order_by: Optional[str] = None, desc: bool = True):
    """Cached version of fetch_records to reduce latency."""
    return fetch_records(table, filters, limit, order_by, desc)


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
    "cached_fetch_records",
    "fetch_latest",
    "update_record",
    "delete_record",
]
