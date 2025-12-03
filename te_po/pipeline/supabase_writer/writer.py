import json
import uuid

from te_po.services.local_storage import save, timestamp


def save_chunk(chunk: str, embedding: list[float], meta: dict) -> str:
    payload = {
        "id": f"chunk_{uuid.uuid4().hex}",
        "chunk_text": chunk,
        "embedding": embedding,
        "metadata": meta,
        "saved_at": timestamp(),
    }
    filename = f"{payload['id']}.json"
    path = save("chunks", filename, json.dumps(payload, indent=2))
    return {"id": payload["id"], "path": path}
