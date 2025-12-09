from fastapi import APIRouter, Body, HTTPException, Query
from te_po.core.config import settings
from te_po.utils.openai_client import client
from te_po.services.vector_service import embed_text, search_text
from te_po.models.vector_models import EmbedRequest, SearchRequest
from pathlib import Path
import json

router = APIRouter(prefix="/vector", tags=["Vector"])


@router.post("/embed")
async def vector_embed(payload: EmbedRequest = Body(...)):
    return embed_text(payload.text)


@router.post("/search")
async def vector_search(payload: SearchRequest = Body(...)):
    return search_text(payload.query, payload.top_k or 5)


@router.post("/retrieval-test")
async def vector_retrieval_test(
    payload: SearchRequest = Body(...),
):
    """Run a simple retrieval against stored embeddings for confidence checks."""
    return search_text(payload.query, payload.top_k or 3)


@router.get("/recent")
async def vector_recent(limit: int = Query(5, ge=1, le=20)):
    """
    Return recent vector logs saved locally (te_po/storage/openai/<glyph>.json).
    Useful for UI 'recent vectors' display.
    """
    log_dir = Path(__file__).resolve().parents[1] / "storage" / "openai"
    entries = []
    if log_dir.exists():
        for f in sorted(log_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8") or "[]")
                if isinstance(data, list):
                    entries.extend(data)
                elif isinstance(data, dict):
                    entries.append(data)
            except Exception:
                continue
            if len(entries) >= limit:
                break
    return {"entries": entries[:limit]}


@router.get("/batch-status")
async def vector_batch_status(
    batch_id: str = Query(..., description="OpenAI vector store file batch id"),
    vector_store_id: str | None = Query(
        None, description="Override vector store id; defaults to OPENAI_VECTOR_STORE_ID env"
    ),
):
    """Check the status of a vector store file batch (GA OpenAI API)."""
    if client is None:
        raise HTTPException(status_code=503, detail="OpenAI client not configured.")
    vs_id = vector_store_id or settings.openai_vector_store_id
    if not vs_id:
        raise HTTPException(status_code=400, detail="Vector store id not configured.")
    try:
        resp = client.vector_stores.file_batches.retrieve(batch_id, vector_store_id=vs_id)
        payload = resp.model_dump() if hasattr(resp, "model_dump") else resp
        return payload
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch batch: {exc}")
