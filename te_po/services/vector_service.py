import json
import os
import tempfile
import uuid
from math import sqrt
from pathlib import Path

from te_po.mauri import MAURI
from te_po.services.local_storage import list_files, load, save, timestamp
from te_po.utils.audit import log_event
from te_po.utils.openai_client import client, DEFAULT_EMBED_MODEL, last_openai_run_id, record_openai_run

VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")
GLYPH = (
    MAURI.get("identity", {}).get("glyph_id")
    or MAURI.get("openai", {}).get("glyph_id")
    or "koru_wolf_blue"
)

def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a)) or 1.0
    norm_b = sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def _push_remote_vector(entry_id: str, text: str, vector, metadata: dict | None = None):
    if client is None or not VECTOR_STORE_ID:
        return {"pushed": False, "reason": "vector store id missing or client offline"}
    if not hasattr(client, "beta") or not hasattr(client.beta, "vector_stores"):
        return {"pushed": False, "reason": "vector store API not available in this client"}

    # GA vector store flow: upload a JSONL file and attach to the store.
    tmp_path = Path(tempfile.gettempdir()) / f"{entry_id}.json"
    record = {
        "id": entry_id,
        "text": text,
        "metadata": metadata or {},
    }
    try:
        tmp_path.write_text(json.dumps(record), encoding="utf-8")
        with open(tmp_path, "rb") as fh:
            file_resp = client.files.create(file=fh, purpose="assistants")
        batch_resp = client.beta.vector_stores.file_batches.create(
            vector_store_id=VECTOR_STORE_ID,
            file_ids=[file_resp.id],
        )
        try:
            batch_payload = (
                batch_resp.model_dump()
                if hasattr(batch_resp, "model_dump")
                else batch_resp.to_dict_recursive()
                if hasattr(batch_resp, "to_dict_recursive")
                else None
            )
        except Exception:
            batch_payload = None

        log_event(
            "vector_batch_enqueued",
            "File attached to vector store",
            source="vector_service",
            data={
                "entry_id": entry_id,
                "vector_store_id": VECTOR_STORE_ID,
                "file_id": file_resp.id,
                "batch_id": getattr(batch_resp, "id", None),
                "status": getattr(batch_resp, "status", None),
            },
        )

        return {
            "pushed": True,
            "reason": None,
            "vector_store_id": VECTOR_STORE_ID,
            "file_id": file_resp.id,
            "batch_id": getattr(batch_resp, "id", None),
            "batch_status": getattr(batch_resp, "status", None),
            "response": batch_payload,
            "openai_run_id": last_openai_run_id(),
        }
    except Exception as exc:
        return {"pushed": False, "reason": str(exc)}
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def embed_text(text: str, metadata: dict | None = None, record_type: str = "embedding"):
    if client is None:
        return {"id": None, "vector": [], "saved": False, "error": "OpenAI client not configured."}
    try:
        rsp = client.embeddings.create(
            model=DEFAULT_EMBED_MODEL,
            input=text,
        )
        record_openai_run(rsp)
        vec = rsp.data[0].embedding
        entry_id = f"vec_{uuid.uuid4().hex}"
        openai_run_id = last_openai_run_id()

        remote = _push_remote_vector(entry_id, text, vec, metadata=metadata)

        save(
            "openai",
            f"{entry_id}.json",
            json.dumps(
                {
                    "id": entry_id,
                    "text": text,
                    "vector": vec,
                    "ts": timestamp(),
                    "type": record_type,
                    "metadata": metadata or {},
                    "remote": remote,
                },
                indent=2,
            ),
        )
        _log_remote(entry_id, text, vec, remote, metadata=metadata)
        return {
            "id": entry_id,
            "vector": vec,
            "saved": True,
            "remote": remote,
            "openai_run_id": openai_run_id,
        }
    except Exception as exc:
        return {"id": None, "vector": [], "saved": False, "error": str(exc)}


def search_text(query: str, top_k=5):
    if client is None:
        return {"matches": [], "error": "OpenAI client not configured."}
    try:
        rsp = client.embeddings.create(
            model=DEFAULT_EMBED_MODEL,
            input=query,
        )
        query_vec = rsp.data[0].embedding
        matches = []
        for filename in list_files("openai"):
            data_raw = load("openai", filename)
            if not data_raw:
                continue
            try:
                record = json.loads(data_raw)
            except json.JSONDecodeError:
                continue
            if record.get("type") != "embedding":
                continue
            vector = record.get("vector")
            if not vector:
                continue
            score = _cosine(query_vec, vector)
            matches.append(
                {
                    "id": record.get("id"),
                    "text": record.get("text"),
                    "score": score,
                    "created_at": record.get("ts"),
                }
            )
        matches.sort(key=lambda item: item["score"], reverse=True)
        return {"matches": matches[:top_k]}
    except Exception as exc:
        return {"matches": [], "error": str(exc)}


def _log_remote(
    entry_id: str,
    text: str,
    vector,
    remote_result: dict,
    vector_store_id: str | None = None,
    chunk_id: str | None = None,
    metadata: dict | None = None,
):
    log_dir = Path(__file__).resolve().parents[1] / "storage" / "openai"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{GLYPH}.json"

    try:
        existing = []
        if log_file.exists():
            existing = json.loads(log_file.read_text(encoding="utf-8") or "[]")
    except Exception:
        existing = []

    record = {
        "id": entry_id,
        "text_length": len(text),
        "dimension": len(vector) if vector else 0,
        "token_estimate": len(text.split()),
        "remote": remote_result,
        "saved_locally": True,
        "timestamp": timestamp(),
        "vector_store_id": vector_store_id or VECTOR_STORE_ID,
        "chunk_id": chunk_id,
        "metadata": metadata or {},
    }
    existing.append(record)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def push_chunk_embedding(
    chunk_id: str,
    text: str,
    embedding: list[float],
    metadata: dict | None = None,
):
    """Push a chunk embedding to OpenAI vector store (if configured) and log the result."""
    if not embedding:
        return {"pushed": False, "reason": "empty embedding"}

    remote = _push_remote_vector(
        entry_id=chunk_id,
        text=text,
        vector=embedding,
        metadata=metadata or {},
    )
    _log_remote(
        entry_id=chunk_id,
        text=text,
        vector=embedding,
        remote_result=remote,
        vector_store_id=VECTOR_STORE_ID,
        chunk_id=chunk_id,
    )
    return remote
