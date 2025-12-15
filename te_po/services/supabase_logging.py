"""
Best-effort helpers to write pipeline/chat/audit events into Supabase tables.
All functions are no-ops if the Supabase client is not configured.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from te_po.utils.supabase_client import get_client


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_audit_event(event: str, detail: str, source: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
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
):
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table("kitenga_pipeline_runs").insert(
            {
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
        ).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def log_chunks_metadata(
    chunks: List[Dict[str, Any]],
    vector_store_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    chunks: list of dicts with keys id, length, hash, remote (optional)
    """
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    # No dedicated chunk metadata table in trimmed schema; skip to reduce noise.
    if not chunks:
        return {"status": "skipped", "reason": "no chunks"}
    return {"status": "skipped", "reason": "no chunk table configured"}


def log_vector_batch(batch_id: Optional[str], vector_store_id: Optional[str], status: Optional[str], metadata: Optional[Dict[str, Any]] = None):
    if not batch_id:
        return {"status": "skipped", "reason": "no batch_id"}
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table("kitenga_vector_batches").upsert(
            {
                "batch_id": batch_id,
                "vector_store_id": vector_store_id,
                "status": status,
                "metadata": metadata or {},
                "updated_at": _now(),
                "created_at": _now(),
            }
        ).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


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
):
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table("kitenga_chat_logs").insert(
            {
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
        ).execute()
        if tool_outputs:
            _persist_taonga_metadata(client, tool_outputs, metadata)
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
    if not rows:
        return
    try:
        client.table("taonga_metadata").insert(rows).execute()
    except Exception:
        # best-effort; ignore failures
        pass
