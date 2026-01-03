"""
Assistant- and tool-related orchestration services for Kitenga.

These functions keep FastAPI routes thin while preserving existing domain flows.
"""

from __future__ import annotations

import base64
import uuid
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException, status
from openai import AsyncOpenAI

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.services.vector_service import embed_text, search_text
from te_po.pipeline.ocr.stealth_engine import StealthOCR
from te_po.services.chat_memory import record_turn, retrieve_context
from te_po.services.project_state_service import get_project_state, format_project_state_for_context
from te_po.utils.audit import log_event
from te_po.services.supabase_logging import log_chat_entry
from te_po.utils.supabase_client import get_client
from te_po.utils.openai_client import (
    DEFAULT_BACKEND_MODEL,
    DEFAULT_VISION_MODEL,
    client,
    generate_text,
    translate_text,
)
from te_po.kitenga.assistant_runtime import (
    extract_message_text,
    poll_assistant_run,
    latest_assistant_message,
)


stealth_ocr_engine = StealthOCR()
SUPA = get_client()
async_openai_client: AsyncOpenAI | None = None
try:
    async_openai_client = AsyncOpenAI()
except Exception:
    async_openai_client = None


def vision_ocr_flow(payload, *, pipeline_source: str | None) -> Dict[str, Any]:
    if client is None:
        raise HTTPException(status_code=503, detail="OpenAI client not configured.")

    _validate_base64(payload.image_base64)
    image_url = f"data:image/png;base64,{payload.image_base64}"
    extracted = _run_openai_vision(image_url)

    vector_result = embed_text(extracted) if payload.save_vector and extracted else None
    pipeline_result = None
    if payload.run_pipeline and extracted:
        pipeline_result = run_pipeline(
            extracted.encode("utf-8"),
            filename=f"vision_{uuid.uuid4().hex}.txt",
            source=pipeline_source or "kitenga_vision",
        )

    log_event(
        "kitenga_vision_ocr",
        "Vision OCR completed",
        source=pipeline_source or "kitenga_vision",
        data={
            "save_vector": payload.save_vector,
            "run_pipeline": payload.run_pipeline,
            "vector": vector_result,
            "pipeline": pipeline_result,
        },
    )

    return {
        "status": "ok",
        "extracted_text": extracted,
        "vector": vector_result,
        "pipeline": pipeline_result,
    }


def whisper_flow(payload, *, run_pipeline_flag: bool, allow_taonga_store: bool) -> Dict[str, Any]:
    text = payload.whisper.strip()
    if not text:
        raise HTTPException(status_code=400, detail="whisper text required")

    pipeline_result = None
    if run_pipeline_flag:
        pipeline_result = run_pipeline(
            text.encode("utf-8"),
            filename=f"whisper_{uuid.uuid4().hex}.txt",
            source=payload.source or "kitenga_whisper",
            mode=payload.mode,
            allow_taonga_store=allow_taonga_store,
        )

    embedding_vector = embed_text(text) if payload.save_vector else None
    retrieval = retrieve_context(text, session_id=payload.session_id) if payload.use_retrieval else None
    translated = translate_text(text, "en") if payload.use_openai_translation else None
    summary = generate_text(
        [{"role": "user", "content": text}],
        model=DEFAULT_BACKEND_MODEL,
    ) if payload.use_openai_summary else None

    record_turn(
        session_id=payload.session_id or "kitenga_session",
        user_message=text,
        assistant_reply="",
        thread_id=payload.thread_id,
        metadata={"mode": payload.mode, "pipeline": pipeline_result},
    )

    return {
        "status": "ok",
        "pipeline": pipeline_result,
        "embedding": embedding_vector,
        "retrieval": retrieval,
        "translation": translated,
        "summary": summary,
    }


async def assistant_query_flow(payload, *, pipeline_token: str | None = None) -> Dict[str, Any]:
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")

    session_id = payload.session_id or f"kitenga_session_{uuid.uuid4().hex}"
    thread_id = payload.thread_id

    if not thread_id:
        thread = await async_openai_client.beta.threads.create()
        thread_id = getattr(thread, "id", None)

    run = await async_openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=_get_kitenga_assistant_id(),
        additional_instructions=payload.metadata.get("notes") if payload.metadata else None,
    )

    final_run, tool_history = await poll_assistant_run(async_openai_client, thread_id, run.id)
    latest = await latest_assistant_message(async_openai_client, thread_id)
    reply_text = extract_message_text(latest) if latest else ""

    log_chat_entry(
        session_id=session_id,
        thread_id=thread_id,
        user_message=payload.prompt,
        assistant_reply=reply_text,
        mode="assistant",
        metadata={"pipeline_tokened": bool(pipeline_token), "tool_history": tool_history},
        tool_outputs=tool_history,
    )

    return {
        "status": "ok",
        "run": getattr(final_run, "status", None),
        "run_status": getattr(final_run, "status", None),
        "run_id": getattr(final_run, "id", getattr(run, "id", None)),
        "thread_id": thread_id,
        "reply": reply_text,
        "tools": tool_history,
    }


async def handle_assistant_query(payload, *, pipeline_token: str | None = None) -> Dict[str, Any]:
    """Wrapper to keep route handlers thin."""
    return await assistant_query_flow(payload, pipeline_token=pipeline_token)


def search_context(query: str, top_k: int = 5) -> Dict[str, Any]:
    results = search_text(query, top_k=top_k)
    return {"results": results, "count": len(results or [])}


def _run_openai_vision(image_url: str) -> str:
    resp = client.chat.completions.create(
        model=DEFAULT_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all readable text from this image. Return plain text only.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        max_tokens=1200,
    )
    return (resp.choices[0].message.content or "").strip()


def _validate_base64(value: str):
    try:
        base64.b64decode(value)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 payload.") from exc


def _get_kitenga_assistant_id() -> str | None:
    from te_po.core.config import settings  # local import to avoid cycles

    return settings.kitenga_assistant_id or None
