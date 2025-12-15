import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from te_po.services.local_storage import DIRS
from te_po.utils.supabase_client import get_client

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/profiles")
async def document_profiles(limit: int = Query(50, ge=1, le=200)):
    """
    Return recent document profiles from local pipeline logs (best-effort) and Supabase metadata if available.
    """
    profiles: list[dict[str, Any]] = []

    # Local pipeline logs (recent)
    log_dir = DIRS["logs"]
    logs = sorted(log_dir.glob("pipeline_*.json"), reverse=True)
    for log_file in logs[:limit]:
        try:
            entry = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        profiles.append(
            {
                "source": entry.get("source"),
                "raw_file": entry.get("raw_file"),
                "clean_file": entry.get("clean_file"),
                "chunk_ids": entry.get("chunks"),
                "vector_batch_id": entry.get("vector_batch_id"),
            }
        )
    # Supabase metadata (if client available and table exists)
    client = get_client()
    if client:
        try:
            resp = (
                client.table("kitenga_artifacts")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            supa_rows = getattr(resp, "data", None) or []
            profiles.extend(
                {
                    "source": row.get("source"),
                    "raw_path": row.get("raw_path") or row.get("storage_path"),
                    "clean_path": row.get("clean_path") or row.get("storage_path"),
                    "chunk_ids": (row.get("metadata") or {}).get("chunk_ids"),
                    "vector_batch_id": (row.get("metadata") or {}).get("vector_batch_id"),
                    "storage": (row.get("metadata") or {}).get("extra", {}).get("storage"),
                    "title": row.get("file_name"),
                    "summary": row.get("summary_long") or row.get("summary_short"),
                    "storage_url": row.get("storage_url") or (row.get("metadata") or {}).get("storage_url"),
                }
                for row in supa_rows
            )
        except Exception:
            # Table might not exist yet; fall back to local only
            pass

    return {"profiles": profiles[:limit]}
