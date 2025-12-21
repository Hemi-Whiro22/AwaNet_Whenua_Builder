from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

_memory_store: List[dict] = []


def _build_matches(realm: str, query: str, top_k: int = 3):
    return [
        {
            "id": f"mem_{idx}",
            "content": f"Simulated match for '{query}' in {realm}",
            "similarity": round(0.95 - idx * 0.1, 3),
            "tapulevel": idx,
        }
        for idx in range(min(top_k, 3))
    ]


class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="Text to semantically search.")
    realm: str = Field("te_ao", description="Realm to search in.")


@router.post("/search")
async def memory_search(req: MemorySearchRequest):
    query = req.query
    realm = req.realm
    matches = _build_matches(realm=realm, query=query)
    return {
        "query": query,
        "realm": realm,
        "matches": matches,
    }


@router.post("/store")
def store_fragment(
    realm: str = "te_ao", content: str = "", tapu_level: int = 0
):
    fragment = {
        "realm": realm,
        "content": content,
        "tapu_level": tapu_level,
    }
    _memory_store.append(fragment)
    return fragment
