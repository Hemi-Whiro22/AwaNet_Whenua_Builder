"""
Chat memory helpers: embed chat turns and retrieve session-scoped context.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

from te_po.services.local_storage import list_files, load
from te_po.services.vector_service import embed_text, _cosine
from te_po.utils.audit import log_event
from te_po.services.supabase_logging import log_chat_entry
from te_po.services.local_storage import timestamp


def record_turn(
    session_id: str,
    thread_id: str | None,
    role: str,
    text: str,
    mode: str | None,
    source: str | None,
):
    """
    Embed and persist a chat turn (user or assistant).
    Uses OpenAI embeddings + vector store push; also logs to Supabase chat logs.
    """
    metadata = {
        "session_id": session_id,
        "thread_id": thread_id,
        "role": role,
        "mode": mode,
        "source": source,
        "ts": timestamp(),
    }
    embed_result = embed_text(text, metadata=metadata, record_type="chat_embedding")
    try:
        log_chat_entry(
            session_id=session_id,
            thread_id=thread_id,
            user_message=text if role == "user" else None,
            assistant_reply=text if role != "user" else None,
            mode=mode,
            vector_batch_id=None,
            pipeline_result=None,
            metadata={"role": role, "source": source, "embed": embed_result},
        )
    except Exception:
        pass
    try:
        log_event(
            "chat_memory_turn",
            "Chat turn embedded",
            source=source,
            data={"session_id": session_id, "role": role, "embed": embed_result},
        )
    except Exception:
        pass
    return embed_result


def retrieve_context(query: str, session_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-K chat turns for this session_id using local embeddings (cosine similarity).
    """
    from te_po.utils.openai_client import client as oa_client

    try:
        q_embed = oa_client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding if oa_client else None
    except Exception:
        q_embed = None

    if not q_embed:
        return []

    matches = []
    for fname in list_files("openai"):
        raw = load("openai", fname)
        if not raw:
            continue
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if rec.get("type") != "chat_embedding":
            continue
        meta = rec.get("metadata") or {}
        if meta.get("session_id") != session_id:
            continue
        vec = rec.get("vector")
        if not vec:
            continue
        score = _cosine(q_embed, vec)
        matches.append(
            {
                "text": rec.get("text"),
                "role": meta.get("role"),
                "ts": meta.get("ts"),
                "session_id": session_id,
                "thread_id": meta.get("thread_id"),
                "score": score,
            }
        )

    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches[:top_k]
