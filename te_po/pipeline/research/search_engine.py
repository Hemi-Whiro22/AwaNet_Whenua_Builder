import json
from math import sqrt
from typing import List, Dict

from te_po.pipeline.embedder.embed_engine import embed_text
from te_po.services.local_storage import list_files, load


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a)) or 1.0
    norm_b = sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def research_query(query: str, limit: int = 10) -> list[Dict]:
    query_embedding = embed_text(query)
    matches: list[Dict] = []
    for filename in list_files("chunks"):
        data_raw = load("chunks", filename)
        if not data_raw:
            continue
        try:
            record = json.loads(data_raw)
        except json.JSONDecodeError:
            continue
        embedding = record.get("embedding")
        if not embedding:
            continue
        similarity = _cosine(query_embedding, embedding)
        matches.append(
            {
                "id": record.get("id"),
                "text": record.get("chunk_text"),
                "metadata": record.get("metadata", {}),
                "score": similarity,
            }
        )
    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]
