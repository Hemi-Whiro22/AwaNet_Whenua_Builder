import json
from datetime import datetime
from typing import List, Dict, Any

from te_po.services.local_storage import list_files, load
from te_po.services.vector_service import search_text


def _format_timestamp(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y%m%d_%H%M%S").isoformat()
    except ValueError:
        return raw


def list_memories(limit: int = 10) -> List[Dict[str, Any]]:
    """Return the most recent stored embeddings/logs as memory entries."""
    entries: List[Dict[str, Any]] = []
    for filename in sorted(list_files("openai"), reverse=True):
        data_raw = load("openai", filename)
        if not data_raw:
            continue
        try:
            record = json.loads(data_raw)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "embedding":
            continue
        entries.append(
            {
                "id": record.get("id"),
                "content": record.get("text"),
                "created_at": _format_timestamp(record.get("ts")),
            }
        )
        if len(entries) >= limit:
            break
    return entries


def retrieve_memories(query: str, top_k: int = 5, min_similarity: float = 0.0) -> List[Dict[str, Any]]:
    """Use vector search to return the closest stored embeddings."""
    result = search_text(query, top_k or 5)
    matches = result.get("matches", [])
    if not matches:
        return []
    filtered = []
    threshold = min_similarity or 0.0
    for match in matches:
        score = match.get("score", 0.0)
        if score < threshold:
            continue
        filtered.append(
            {
                "id": match.get("id"),
                "content": match.get("text"),
                "similarity": score,
                "created_at": _format_timestamp(match.get("created_at")),
            }
        )
    return filtered
