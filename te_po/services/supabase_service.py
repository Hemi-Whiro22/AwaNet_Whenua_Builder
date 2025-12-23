"""Consolidated Supabase client and helpers for pipeline and logging."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from mimetypes import guess_type
from pathlib import Path
from typing import Any, Dict, List, Optional

from te_po.utils.supabase_client import (
    get_client as _get_client,
    insert_record as client_insert_record,
    fetch_records as client_fetch_records,
    cached_fetch_records as client_cached_fetch_records,
    fetch_latest as client_fetch_latest,
    update_record as client_update_record,
    delete_record as client_delete_record,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_client():
    return _get_client()


def fetch_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    order_by: Optional[str] = None,
    desc: bool = True,
) -> Dict[str, Any]:
    return client_fetch_records(table, filters=filters, limit=limit, order_by=order_by, desc=desc)


def cached_fetch_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    order_by: Optional[str] = None,
    desc: bool = True,
) -> Dict[str, Any]:
    return client_cached_fetch_records(table, filters=filters, limit=limit, order_by=order_by, desc=desc)


def fetch_latest(table: str, order_by: str = "created_at") -> Dict[str, Any]:
    return client_fetch_latest(table, order_by=order_by)


def update_record(table: str, filters: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
    return client_update_record(table, filters, values)


def delete_record(table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    return client_delete_record(table, filters)


def insert_record(table: str, record: Dict[str, Any], upsert: bool = False):
    return client_insert_record(table, record, upsert=upsert)


def record_file_metadata(
    source: str,
    raw_path: Optional[str],
    clean_path: Optional[str],
    chunks: List[str],
    vector_batch_id: Optional[str],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    table = "kitenga_artifacts"
    payload = {
        "source": source,
        "file_name": (clean_path or raw_path or "").split("/")[-1] if (clean_path or raw_path) else None,
        "storage_path": clean_path or raw_path,
        "summary_short": (extra or {}).get("summary_short") if extra else None,
        "summary_long": (extra or {}).get("summary_long") if extra else None,
        "metadata": {
            "chunk_ids": chunks,
            "vector_batch_id": vector_batch_id,
            "raw_path": raw_path,
            "clean_path": clean_path,
            "extra": extra or {},
        },
    }
    try:
        resp = client.table(table).upsert(payload).execute()
        return {"status": "ok", "table": table, "response": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def upload_file(local_path: str, dest_path: str, bucket: Optional[str] = None) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    bucket_name = bucket or os.getenv("SUPABASE_BUCKET_STORAGE", "tepo_storage")
    try:
        path_obj = Path(local_path)
        if not path_obj.exists():
            from te_po.services.local_storage import DIRS  # avoid circular import

            for key in ("raw", "clean", "chunks"):
                candidate = DIRS[key] / local_path
                if candidate.exists():
                    path_obj = candidate
                    break
        with path_obj.open("rb") as fh:
            client.storage.from_(bucket_name).upload(
                dest_path,
                fh,
                {"upsert": "true", "cacheControl": "3600"},
            )
        return {"status": "ok", "bucket": bucket_name, "path": dest_path}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def upload_bytes(data: bytes, dest_path: str, bucket: Optional[str] = None) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    bucket_name = bucket or os.getenv("SUPABASE_BUCKET_STORAGE", "tepo_storage")
    try:
        client.storage.from_(bucket_name).upload(
            dest_path,
            data,
            {"upsert": "true", "cacheControl": "3600"},
        )
        return {"status": "ok", "bucket": bucket_name, "path": dest_path}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def hash_file(path: str) -> Optional[str]:
    try:
        h = sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def detect_content_type(path: str) -> Optional[str]:
    ctype, _ = guess_type(path)
    return ctype


def _upsert(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table(table).upsert(row).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def log_audit_event(event: str, detail: str, source: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table("kitenga_logs").insert(
            {
                "event": event,
                "detail": detail,
                "source": source,
                "data": data or {},
                "created_at": _now(),
            }
        ).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def log_pipeline_run(
    source: str,
    status: str,
    glyph: Optional[str],
    raw_file: Optional[str],
    clean_file: Optional[str],
    chunk_ids: List[str],
    vector_batch_id: Optional[str],
    storage: Optional[Dict[str, Any]] = None,
    supabase_status: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    row = {
        "source": source,
        "status": status,
        "glyph": glyph,
        "raw_file": raw_file,
        "clean_file": clean_file,
        "chunk_ids": chunk_ids,
        "vector_batch_id": vector_batch_id,
        "storage": storage,
        "supabase_status": supabase_status,
        "metadata": metadata or {},
        "created_at": _now(),
    }
    return _upsert("kitenga_pipeline_runs", row)


def log_chunks_metadata(
    chunks: List[Dict[str, Any]],
    vector_store_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not chunks:
        return {"status": "skipped", "reason": "no chunks"}
    return {"status": "skipped", "reason": "chunk table not configured"}


def log_vector_batch(
    batch_id: Optional[str],
    vector_store_id: Optional[str],
    status: Optional[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not batch_id:
        return {"status": "skipped", "reason": "no batch_id"}
    row = {
        "batch_id": batch_id,
        "vector_store_id": vector_store_id,
        "status": status,
        "metadata": metadata or {},
        "updated_at": _now(),
        "created_at": _now(),
    }
    return _upsert("kitenga_vector_batches", row)


def log_chat_entry(
    session_id: str,
    thread_id: Optional[str],
    user_message: str,
    assistant_reply: str,
    mode: Optional[str] = None,
    vector_batch_id: Optional[str] = None,
    pipeline_result: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tool_outputs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    row = {
        "session_id": session_id,
        "thread_id": thread_id,
        "user_message": user_message,
        "assistant_reply": assistant_reply,
        "mode": mode,
        "vector_batch_id": vector_batch_id,
        "pipeline_result": pipeline_result,
        "metadata": metadata or {},
        "created_at": _now(),
    }
    resp = _insert_row("kitenga_chat_logs", row)
    if tool_outputs:
        _persist_taonga_metadata(get_client(), tool_outputs, metadata)
    return resp


def _insert_row(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table(table).insert(row).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def _safe_tool_blob(blob: Any) -> str:
    if blob is None:
        return ""
    if isinstance(blob, str):
        return blob
    try:
        return json.dumps(blob, ensure_ascii=False)
    except Exception:
        return str(blob)


def _persist_taonga_metadata(client, tool_outputs: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]]):
    if client is None:
        return
    rows = []
    now = _now()
    base_source = (metadata or {}).get("source") or (metadata or {}).get("route")
    for entry in tool_outputs or []:
        if not entry:
            continue
        name = entry.get("tool") or entry.get("name") or entry.get("function", {}).get("name") or "assistant_tool"
        payload = entry.get("result")
        if payload is None:
            payload = entry.get("output") or entry.get("reason")
        description = _safe_tool_blob(payload)
        source = entry.get("source") or base_source or name
        rows.append(
            {
                "name": name[:255] if isinstance(name, str) else "assistant_tool",
                "description": description[:4000],
                "cultural_significance": entry.get("status"),
                "source": source,
                "category": "assistant_tool",
                "created_at": now,
                "updated_at": now,
            }
        )
    try:
        client.table("taonga_metadata").insert(rows).execute()
    except Exception:
        pass


__all__ = [
    "get_client",
    "record_file_metadata",
    "upload_file",
    "upload_bytes",
    "hash_file",
    "detect_content_type",
    "log_audit_event",
    "log_pipeline_run",
    "log_chunks_metadata",
    "log_vector_batch",
    "log_chat_entry",
    "insert_record",
    "fetch_records",
    "cached_fetch_records",
    "fetch_latest",
    "update_record",
    "delete_record",
]
