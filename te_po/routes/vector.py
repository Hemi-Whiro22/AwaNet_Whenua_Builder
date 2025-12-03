from fastapi import APIRouter, Body
from te_po.services.vector_service import embed_text, search_text
from te_po.models.vector_models import EmbedRequest, SearchRequest

router = APIRouter(prefix="/vector", tags=["Vector"])


@router.post("/embed")
async def vector_embed(payload: EmbedRequest = Body(...)):
    return embed_text(payload.text)


@router.post("/search")
async def vector_search(payload: SearchRequest = Body(...)):
    return search_text(payload.query, payload.top_k or 5)
