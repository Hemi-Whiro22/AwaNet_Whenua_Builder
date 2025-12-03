from pydantic import BaseModel


class MemoryQuery(BaseModel):
    query: str
    top_k: int | None = 5
    min_similarity: float | None = 0.0
