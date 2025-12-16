from __future__ import annotations

import logging
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List, Optional

import os

from te_po.core.config import settings

try:
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover - library optional in test env
    Client = None  # type: ignore
    create_client = None  # type: ignore

logger = logging.getLogger("te_po.supabase")


@lru_cache(maxsize=1)
def _build_client() -> Optional["Client"]:
    """
    Instantiate a Supabase client once per process.
    Uses the service role key when available; falls back to generic SUPABASE_KEY.
    """
    if create_client is None:
        logger.warning("Supabase client library not installed.")
        return None

    url = settings.supabase_url or os.getenv("SUPABASE_URL") or ""
    key = (
        settings.supabase_service_role_key
        or os.getenv("SUPABASE_KEY")
        or getattr(settings, "supabase_publishable_key", None)
        or settings.supabase_anon_key
        or ""
    )

    if not url or not key:
        logger.error("Supabase configuration missing URL or API key.")
        return None

    try:
        return create_client(url, key)
    except Exception as exc:  # pragma: no cover - network failure
        logger.error("Failed to initialize Supabase client: %s", exc)
        return None


def get_client() -> Optional["Client"]:
    """Return the cached Supabase client instance (or None when unavailable)."""
    return _build_client()


def insert_with_realm(table: str, payload: Dict[str, Any], realm_id: str) -> Optional[Dict[str, Any]]:
    """
    Insert a record into a table, attaching realm_id. Returns Supabase payload or None.
    """
    client = get_client()
    if client is None:
        logger.debug("Supabase client unavailable; insert skipped for table %s.", table)
        return None

    record = deepcopy(payload)
    record["realm_id"] = realm_id
    try:
        response = client.table(table).insert(record).execute()
        return getattr(response, "data", None) if response else None
    except Exception as exc:  # pragma: no cover - network failure
        logger.error("Failed to insert into %s for realm %s: %s", table, realm_id, exc)
        return None


def select_by_realm(table: str, realm_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch records for a realm from the specified table.
    Returns an empty list when the client is unavailable.
    """
    client = get_client()
    if client is None:
        logger.debug("Supabase client unavailable; select skipped for table %s.", table)
        return []
    try:
        response = (
            client.table(table)
            .select("*")
            .eq("realm_id", realm_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return getattr(response, "data", None) or []
    except Exception as exc:  # pragma: no cover - network failure
        logger.error("Failed to fetch from %s for realm %s: %s", table, realm_id, exc)
        return []


__all__ = ["get_client", "insert_with_realm", "select_by_realm"]
