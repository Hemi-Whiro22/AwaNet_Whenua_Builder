from pydantic import BaseModel
from typing import List, Optional


class EmbedRequest(BaseModel):
    text: str


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class VectorResult(BaseModel):
    id: str
    vector: list
    saved: bool


class SearchResult(BaseModel):
    matches: List[dict]
