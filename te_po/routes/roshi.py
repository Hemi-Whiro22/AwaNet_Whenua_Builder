from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException
from typing import Any, Dict, List
import math

from te_po.services.vector_service import embed_text
from te_po.utils.supabase_client import get_client

router = APIRouter(prefix="/roshi", tags=["Cards", "Vector"])


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def search_similar_cards(query_vec: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
    client = get_client()
    if client is None:
        return []
    try:
        # Limit fetch to recent rows to avoid huge payloads
        resp = (
            client.table("card_context_index")
            .select("id,card_id,embedding,context_text,image_url,brave_snippet,ebay_link,card_name,card_number,series,value_estimate")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )
        rows = getattr(resp, "data", None) or []
    except Exception:
        return []

    scored = []
    for row in rows:
        vec = row.get("embedding") or []
        if not vec or not isinstance(vec, list):
            continue
        try:
            score = _cosine(query_vec, vec)
        except Exception:
            continue
        scored.append(
            {
                "id": row.get("id"),
                "card_id": row.get("card_id"),
                "card_name": row.get("card_name"),
                "card_number": row.get("card_number"),
                "series": row.get("series"),
                "value_estimate": row.get("value_estimate"),
                "context_text": row.get("context_text"),
                "image_url": row.get("image_url"),
                "brave_snippet": row.get("brave_snippet"),
                "ebay_link": row.get("ebay_link"),
                "score": score,
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


@router.post("/query_card_context")
async def query_card_context(payload: Dict[str, Any] = Body(...)):
    """
    Vector search over card_context_index. Body: { query: "text" }
    """
    query = (payload.get("query") or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    embed_res = embed_text(query)
    query_vec = embed_res.get("vector") if isinstance(embed_res, dict) else None
    if not query_vec:
        return {"results": [], "error": embed_res.get("error") if isinstance(embed_res, dict) else "no embedding"}

    matches = search_similar_cards(query_vec, top_k=10)
    return {"results": matches}
