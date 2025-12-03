from fastapi import APIRouter, Body

from te_po.models.memory_models import MemoryQuery
from te_po.services.memory_service import list_memories, retrieve_memories

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/")
async def memory_index():
    return list_memories()


@router.post("/retrieve")
async def memory_retrieve(payload: MemoryQuery = Body(...)):
    return retrieve_memories(
        payload.query,
        payload.top_k or 5,
        payload.min_similarity or 0.0,
    )
