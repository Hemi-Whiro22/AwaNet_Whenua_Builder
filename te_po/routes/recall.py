from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException, Path, status
from pydantic import BaseModel, Field

from te_po.schema.realms import RealmConfigLoader, RealmConfigError, RealmNotFoundError
from te_po.utils.recall_service import RecallService


class RecallRequest(BaseModel):
    query: str = Field(..., description="User query to recall context for.")
    thread_id: str | None = Field(default=None, description="Optional thread/session identifier.")
    top_k: int | None = Field(default=None, ge=1, le=50, description="Maximum matches to return.")
    vector_store: str | None = Field(
        default=None, description="Vector store backend hint (e.g., 'supabase', 'openai')."
    )


router = APIRouter(tags=["Recall"])


@router.post(
    "/{realm_id}/recall",
    summary="Retrieve realm-scoped recall matches.",
)
async def realm_recall(
    realm_id: str = Path(..., description="Identifier for the realm (e.g., researcher)."),
    payload: RecallRequest = Body(...),
):
    try:
        realm_config = RealmConfigLoader.get(realm_id)
    except RealmNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Realm '{realm_id}' not found."
        ) from exc
    except RealmConfigError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    if not realm_config.supports_recall:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Recall disabled for realm '{realm_id}'.",
        )

    service = RecallService(realm_config)
    try:
        result = service.recall(
            query=payload.query,
            thread_id=payload.thread_id,
            top_k=payload.top_k,
            vector_store=payload.vector_store,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {
        "realm_id": result.get("realm_id"),
        "matches": result.get("matches", []),
        "query_tokens": result.get("query_tokens"),
        "recall_latency_ms": result.get("recall_latency_ms"),
        "backend": result.get("backend"),
        "top_k": result.get("top_k"),
    }
