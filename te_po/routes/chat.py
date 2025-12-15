from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from te_po.core.config import settings
from te_po.utils.supabase_client import get_client
from te_po.utils.openai_client import client as oa_client, DEFAULT_BACKEND_MODEL, generate_text
from te_po.services.vector_service import embed_text
from te_po.services.chat_memory import retrieve_context
from te_po.utils.audit import log_event

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/save-session")
async def save_session(
    session_id: str,
    title: Optional[str] = None,
    tags: Optional[str] = None,
    summarize: bool = True,
    summary_words: int = 300,
    write_ari: bool = False,
):
    """
    Finalize/save a chat session: optional summary, tag, and store in Supabase logs.
    - session_id: chat session identifier
    - title: optional human-friendly title
    - tags: optional comma-separated tags
    - summarize: when true, attempts an OpenAI summary of session context
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    supabase = get_client()
    chat_rows = []
    if supabase is not None:
        try:
            resp = (
                supabase.table("kitenga_chat_logs")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .limit(20)
                .execute()
            )
            chat_rows = getattr(resp, "data", None) or []
        except Exception:
            chat_rows = []

    # Fallback summary input: combine latest chat rows or retrieved context
    convo_text = ""
    if chat_rows:
        chunks = []
        for row in chat_rows:
            role = row.get("mode") or "chat"
            user_msg = row.get("user_message") or ""
            assistant_reply = row.get("assistant_reply") or ""
            if user_msg:
                chunks.append(f"[user] {user_msg}")
            if assistant_reply:
                chunks.append(f"[assistant] {assistant_reply}")
        convo_text = "\n".join(chunks)[-12000:]
    else:
        matches = retrieve_context("", session_id=session_id, top_k=10) or []
        chunks = [f"[{m.get('role','user')}] {m.get('text','')}" for m in matches]
        convo_text = "\n".join(chunks)[-12000:]

    summary = None
    summary_vector = None
    if summarize and oa_client is not None and convo_text.strip():
        try:
            summary = generate_text(
                model=DEFAULT_BACKEND_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"Summarize the chat session in clear paragraphs, focused on decisions, findings, and TODOs. Keep it under {summary_words} words.",
                    },
                    {"role": "user", "content": convo_text},
                ],
                max_tokens=600,
            )
            try:
                summary_vector = embed_text(
                    summary,
                    metadata={"session_id": session_id, "title": title or "", "mode": "research"},
                    record_type="chat_summary",
                )
            except Exception:
                summary_vector = None
        except Exception:
            summary = None

    log_event(
        "chat_session_saved",
        "Chat session saved/finalized",
        source="chat_save_session",
        data={"session_id": session_id, "title": title, "tags": tags, "summary": summary},
    )

    if supabase is not None:
        try:
            supabase.table("tepo_logs").insert(
                {
                    "event": "chat_session_saved",
                    "detail": title or "chat session saved",
                    "source": "chat_save_session",
                    "data": {"session_id": session_id, "tags": tags, "summary": summary},
                }
            ).execute()
        except Exception:
            pass
        # Optional: write to ari_whakapapa (best-effort, for research mode)
        if write_ari and summary:
            try:
                supabase.table("ari_whakapapa").insert(
                    {
                        "title": title or f"Chat session {session_id}",
                        "summary_text": summary,
                        "tags": tags,
                        "mode": "research",
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    }
                ).execute()
            except Exception:
                pass

    return {
        "status": "ok",
        "session_id": session_id,
        "title": title,
        "tags": tags,
        "summary": summary,
        "summary_vector": summary_vector,
    }
