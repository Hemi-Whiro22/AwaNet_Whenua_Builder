from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from hashlib import sha256 as _sha256
from mimetypes import guess_type
from te_po.core.config import settings
from te_po.utils.supabase_client import get_client


def record_file_metadata(
    source: str,
    raw_path: Optional[str],
    clean_path: Optional[str],
    chunks: List[str],
    vector_batch_id: Optional[str],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Best-effort upsert of pipeline metadata into Supabase table.
    Does NOT upload files; only records paths/ids.
    """
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}

    # Hard-code to Kitenga artifacts table (public.kitenga_artifacts)
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


def upload_file(
    local_path: str,
    dest_path: str,
    bucket: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Upload a file to Supabase storage. Returns metadata; best-effort.
    """
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    bucket_name = bucket or settings.supabase_bucket_storage or "tepo_storage"
    try:
        path_obj = Path(local_path)
        # If relative, try common storage dirs
        if not path_obj.exists():
            from te_po.services.local_storage import DIRS
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


def upload_bytes(
    data: bytes,
    dest_path: str,
    bucket: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload raw bytes to Supabase storage."""
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    bucket_name = bucket or settings.supabase_bucket_storage or "tepo_storage"
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
        h = _sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def detect_content_type(path: str) -> Optional[str]:
    ctype, _ = guess_type(path)
    return ctype
