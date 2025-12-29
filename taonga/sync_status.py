from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from te_po.utils.supabase_client import get_client


def _execute_query(query: Any) -> Tuple[List[Dict[str, Any]], Optional[int], Optional[Any]]:
    try:
        resp = query.execute()
    except Exception as exc:
        return [], None, str(exc)

    error = getattr(resp, "error", None)
    data = getattr(resp, "data", None) or []
    count = None
    try:
        body = resp.json()
        count = body.get("count")
    except Exception:
        pass
    return data, count, error


def fetch_analysis_sync_status() -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "supabase_unavailable"}

    table_query = (
        client.schema("kitenga")
        .table("payload_registry")
        .select("table_name, schema_name, synced_at", count="exact")
        .order("synced_at", desc=True)
        .limit(1)
    )
    tables, table_count, table_error = _execute_query(table_query)
    if table_error:
        return {"status": "error", "error": table_error}

    doc_query = (
        client.schema("kitenga")
        .table("analysis_documents")
        .select("name, format, created_at", count="exact")
        .order("created_at", desc=True)
        .limit(1)
    )
    docs, doc_count, doc_error = _execute_query(doc_query)
    if doc_error:
        return {"status": "error", "error": doc_error}

    return {
        "status": "ok",
        "latest_table": tables[0] if tables else None,
        "tables_count": table_count,
        "latest_document": docs[0] if docs else None,
        "documents_count": doc_count,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }


def fetch_latest_analysis_document_content() -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return {"status": "supabase_unavailable"}
    query = (
        client.schema("kitenga")
        .table("analysis_documents")
        .select("name,format,content,text_content,metadata,created_at")
        .order("created_at", desc=True)
        .limit(1)
    )
    docs, doc_count, error = _execute_query(query)
    if error:
        return {"status": "error", "error": error}
    return {
        "status": "ok",
        "document": docs[0] if docs else None,
        "documents_count": doc_count,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }
