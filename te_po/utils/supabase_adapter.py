from __future__ import annotations

from typing import Any, Dict

from te_po.utils.supabase_client import insert_record, fetch_records, fetch_latest, update_record, delete_record


def insert_den(table: str, record: Dict[str, Any], upsert: bool = False):
    """Wrapper for insert/upsert to Supabase."""
    return insert_record(table, record, upsert=upsert)


__all__ = [
    "insert_den",
    "insert_record",
    "fetch_records",
    "fetch_latest",
    "update_record",
    "delete_record",
]
