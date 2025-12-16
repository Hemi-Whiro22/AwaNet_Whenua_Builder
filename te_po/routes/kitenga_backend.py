"""Kitenga endpoints backed by OpenAI (vision + text) with optional vector persistence."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import time
import uuid
from typing import Any, Dict, List

import requests
import httpx
from fastapi import APIRouter, Body, File, Form, Header, HTTPException, Query, Request, UploadFile, status
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from mcp.types import Tool

from te_po.core.config import settings
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline as exec_pipeline, run_pipeline
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
from te_po.routes.kitenga_tool_router import TOOL_REGISTRY, call_tool_endpoint

router = APIRouter(prefix="/kitenga", tags=["Kitenga"])

MAX_BASE64_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TEXT_LENGTH = 10_000
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")
BRAVE_API_TOKEN = os.getenv("BRAVE_API_WEB_SEARCH") or os.getenv("BRAVE_API_KEY")
CARD_BUCKET = os.getenv("CARD_BUCKET") or "ocr_cards"


class VisionOCRRequest(BaseModel):
    image_base64: str = Field(..., max_length=MAX_BASE64_SIZE)
    save_vector: bool = False
    run_pipeline: bool = False
    pipeline_source: str | None = None


class WhisperRequest(BaseModel):
    whisper: str = Field(..., max_length=MAX_TEXT_LENGTH)
    session_id: str | None = None
    thread_id: str | None = None
    system_prompt: str | None = None
    run_pipeline: bool = False
    save_vector: bool = False
    use_retrieval: bool = False
    use_openai_summary: bool = False
    use_openai_translation: bool = False
    mode: str | None = Field(default="research", description="Mode flag e.g., research or taonga")
    allow_taonga_store: bool = Field(default=False, description="If true, taonga mode still stores/uploads")
    source: str | None = None


class KitengaAskRequest(BaseModel):
    prompt: str = Field(..., max_length=MAX_TEXT_LENGTH)
    session_id: str | None = Field(default=None, description="Supabase logging session id")
    thread_id: str | None = Field(default=None, description="Assistant thread id for continuity")
    metadata: Dict[str, Any] | None = Field(default=None, description="Optional metadata stored in logs")


class OcrToolRequest(BaseModel):
    file_url: str = Field(..., description="Remote URL with the bytes to OCR")
    taonga_mode: bool = Field(default=False, description="Preserve stealth metadata when true")
    prefer_offline: bool = Field(default=True, description="Try local OCR before OpenAI vision")


class TranslateToolRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LENGTH, description="Text to translate")
    target_language: str = Field(default="mi", description="Language code e.g., mi/en")
    context: str | None = Field(default=None, description="Optional translation context or guidance")


try:
    async_openai_client = AsyncOpenAI()
except Exception:
    async_openai_client = None


def _get_kitenga_assistant_id() -> str | None:
    return settings.kitenga_assistant_id or os.getenv("KITENGA_ASSISTANT_ID")


stealth_ocr_engine = StealthOCR()


def _extract_message_text(message) -> str:
    parts: List[str] = []
    for block in getattr(message, "content", []) or []:
        block_type = getattr(block, "type", None)
        if block_type == "text" and hasattr(block, "text"):
            value = getattr(block.text, "value", "")
            if value:
                parts.append(value)
        elif hasattr(block, "value") and isinstance(block.value, str):
            parts.append(block.value)
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def _find_tool_entry(name: str) -> Dict[str, Any] | None:
    name = name or ""
    for entry in TOOL_REGISTRY:
        if entry.get("name") == name:
            return entry
        function_def = entry.get("function") or {}
        if function_def.get("name") == name:
            return entry
    return None


def _tool_output_string(data: Any) -> str:
    try:
        return json.dumps(data, default=str)
    except Exception:
        return json.dumps({"output": str(data)})


async def _fetch_file_bytes(url: str) -> bytes:
    if not url:
        raise HTTPException(status_code=400, detail="file_url is required")
    try:
        async with httpx.AsyncClient(timeout=30) as client_http:
            resp = await client_http.get(url)
            resp.raise_for_status()
            return resp.content
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to fetch file: {exc}")


async def _execute_tool_call(tool_call) -> Dict[str, Any]:
    name = getattr(getattr(tool_call, "function", None), "name", "")
    raw_args = getattr(getattr(tool_call, "function", None), "arguments", "{}")
    try:
        parsed_args = json.loads(raw_args or "{}")
    except Exception:
        parsed_args = {}

    entry = _find_tool_entry(name)
    if entry and entry.get("path"):
        method = entry.get("method", "POST")
        auth = entry.get("auth") or {}
        token_env = auth.get("token_env") if isinstance(auth, dict) else None
        try:
            result = await call_tool_endpoint(entry["path"], method, parsed_args, token_env)
            return {"status": "ok", "tool": name, "result": result}
        except HTTPException as exc:
            return {"status": "error", "tool": name, "reason": exc.detail}
        except Exception as exc:
            return {"status": "error", "tool": name, "reason": str(exc)}
    return {"status": "error", "tool": name, "reason": "tool not configured"}


async def _poll_assistant_run(thread_id: str, run_id: str) -> tuple[Any, List[Dict[str, Any]]]:
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")
    tool_history: List[Dict[str, Any]] = []
    for _ in range(180):
        run = await async_openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )
        status = getattr(run, "status", "unknown")
        if status == "completed":
            return run, tool_history
        if status == "requires_action" and getattr(run, "required_action", None):
            tool_calls = getattr(run.required_action.submit_tool_outputs, "tool_calls", []) or []
            outputs = []
            for call in tool_calls:
                payload = await _execute_tool_call(call)
                tool_history.append(payload)
                outputs.append(
                    {
                        "tool_call_id": getattr(call, "id", uuid.uuid4().hex),
                        "output": _tool_output_string(payload),
                    }
                )
            if outputs:
                await async_openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=outputs,
                )
        elif status in {"failed", "cancelled", "expired"}:
            raise HTTPException(status_code=500, detail=f"Assistant run {status}")
        await asyncio.sleep(1)
    raise HTTPException(status_code=504, detail="Assistant run timeout")


async def _latest_assistant_message(thread_id: str):
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")
    messages = await async_openai_client.beta.threads.messages.list(thread_id=thread_id, limit=5)
    for msg in getattr(messages, "data", []) or []:
        if getattr(msg, "role", "") == "assistant":
            return msg
    return messages.data[0] if getattr(messages, "data", None) else None


def _auth_check(authorization: str | None):
    """Optional bearer enforcement using PIPELINE_TOKEN."""
    if not PIPELINE_TOKEN:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )
    token = authorization.split(" ", 1)[1].strip()
    if token != PIPELINE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
        )


def _validate_base64(value: str):
    try:
        base64.b64decode(value)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 payload.") from exc


@router.post("/vision-ocr")
async def vision_ocr(
    payload: VisionOCRRequest,
    authorization: str | None = Header(default=None),
):
    """Extract text from an image via OpenAI vision; optionally persist to vector store."""
    _auth_check(authorization)
    if client is None:
        raise HTTPException(status_code=503, detail="OpenAI client not configured.")

    _validate_base64(payload.image_base64)
    image_url = f"data:image/png;base64,{payload.image_base64}"

    try:
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
        extracted = (resp.choices[0].message.content or "").strip()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR failed: {exc}")

    vector_result = None
    pipeline_result = None
    if payload.save_vector and extracted:
        vector_result = embed_text(extracted)

    if payload.run_pipeline and extracted:
        pipeline_result = run_pipeline(
            extracted.encode("utf-8"),
            filename=f"vision_{uuid.uuid4().hex}.txt",
            source=payload.pipeline_source or "kitenga_vision",
        )

    log_event(
        "kitenga_vision_ocr",
        "Vision OCR completed",
        source=payload.pipeline_source or "kitenga_vision",
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


class CardScanRequest(BaseModel):
    card_name: str | None = None
    series: str | None = None
    card_number: str | None = None
    rarity: str | None = None
    front_url: str | None = None
    back_url: str | None = None
    tags: list[str] | None = None
    save_processed: bool = True


def _fetch_image(url: str | None) -> bytes | None:
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            return resp.content
    except Exception:
        return None
    return None


def _detect_card_number(text: str) -> str | None:
    patterns = [
        r"[A-Z]{1,3}\d{1,3}-\d{2,3}",  # e.g., BT16-069
        r"\d{3}-\d{3}",
    ]
    for pat in patterns:
        m = re.search(pat, text.upper())
        if m:
            return m.group(0)
    return None


def _detect_rarity(text: str) -> str | None:
    rarities = ["SCR", "SPR", "SR", "UR", "SSR", "R", "UC", "C", "COMMON", "UNCOMMON", "RARE"]
    for r in rarities:
        if re.search(rf"\b{r}\b", text.upper()):
            return r
    return None


def _estimate_price_brave(card_name: str | None, card_number: str | None) -> dict:
    if not BRAVE_API_TOKEN or not card_name:
        return {"estimate": None, "source": None}
    query_parts = [card_name]
    if card_number:
        query_parts.append(card_number)
    query_parts.append("price")
    query = " ".join([p for p in query_parts if p])
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_TOKEN},
            params={"q": query, "count": 5},
            timeout=8,
        )
        if not resp.ok:
            return {"estimate": None, "source": None}
        data = resp.json() or {}
        web_results = data.get("web", {}).get("results", [])
        price_val = None
        price_source = None
        for item in web_results:
            text = " ".join([item.get("title") or "", item.get("description") or ""])
            m = re.search(r"\$([0-9.,]+)", text)
            if m:
                raw = m.group(1).replace(",", "")
                try:
                    price_val = float(raw)
                    price_source = item.get("url")
                    break
                except Exception:
                    continue
        return {"estimate": price_val, "source": price_source, "results": web_results}
    except Exception:
        return {"estimate": None, "source": None}


def _upload_supabase_bytes(client, bucket: str, dest_path: str, data: bytes) -> str | None:
    try:
        client.storage.from_(bucket).upload(dest_path, data)
        return dest_path
    except Exception:
        return None


# Accept back image as optional for richer OCR
@router.post("/cards/scan", tags=["Cards", "OCR Pipeline"])
async def scan_cards(
    request: Request,
    front: UploadFile | None = File(default=None),
    back: UploadFile | None = File(default=None),
    payload: CardScanRequest | None = Body(default=None),
):
    """
    Scan DBS cards (front/back), extract metadata, estimate value, and persist to Supabase.
    - Accepts multipart with front/back UploadFile or JSON with URLs.
    - Uses StealthOCR -> parsed metadata -> optional Brave price estimate.
    - Stores raw/process artifacts in Supabase bucket `ocr_cards` and rows in `card_scans`.
    """
    body = payload
    if body is None:
        try:
            data = await request.json()
            body = CardScanRequest(**data)
        except Exception:
            body = CardScanRequest()

    front_bytes = None
    back_bytes = None

    if front is not None:
        front_bytes = await front.read()
    elif body and body.front_url:
        front_bytes = _fetch_image(body.front_url)

    if back is not None:
        back_bytes = await back.read()
    elif body and body.back_url:
        back_bytes = _fetch_image(body.back_url)

    if not front_bytes and not back_bytes:
        raise HTTPException(status_code=400, detail="Provide a front or back image (file upload or URL).")

    scanner = StealthOCR()
    scanner.cultural_encoding_active = False  # avoid cultural encoding for trading cards

    def run_scan(img_bytes: bytes | None):
        if not img_bytes:
            return None
        return scanner.real_scan(img_bytes)

    front_scan = run_scan(front_bytes)
    back_scan = run_scan(back_bytes)
    merged_text = " ".join(
        filter(None, [front_scan.get("text_extracted") if front_scan else "", back_scan.get("text_extracted") if back_scan else ""])
    )

    card_name = body.card_name or (merged_text.split("\n")[0].strip() if merged_text else None)
    card_number = body.card_number or _detect_card_number(merged_text)
    rarity = body.rarity or _detect_rarity(merged_text)
    series = body.series
    tags = body.tags or []

    price_info = _estimate_price_brave(card_name, card_number)

    supabase = get_client()
    record_id = str(uuid.uuid4())
    storage = {}
    processed_path = None

    if supabase:
        try:
            if front_bytes:
                path = f"raw/{record_id}_front.jpg"
                uploaded = _upload_supabase_bytes(supabase, CARD_BUCKET, path, front_bytes)
                storage["front"] = uploaded
            if back_bytes:
                path = f"raw/{record_id}_back.jpg"
                uploaded = _upload_supabase_bytes(supabase, CARD_BUCKET, path, back_bytes)
                storage["back"] = uploaded
        except Exception:
            storage = {}

        if body.save_processed:
            try:
                processed_path = f"processed/{(card_name or 'card').replace(' ', '_')}_{record_id}.json"
                payload = {
                    "id": record_id,
                    "card_name": card_name,
                    "series": series,
                    "card_number": card_number,
                    "rarity": rarity,
                    "front_scan": front_scan,
                    "back_scan": back_scan,
                    "price": price_info,
                    "tags": tags,
                }
                _upload_supabase_bytes(supabase, CARD_BUCKET, processed_path, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except Exception:
                processed_path = None

        try:
            supabase.table("card_scans").insert(
                {
                    "id": record_id,
                    "card_name": card_name,
                    "series": series,
                    "card_number": card_number,
                    "rarity": rarity,
                    "front_url": storage.get("front") or (body.front_url if body else None),
                    "back_url": storage.get("back") or (body.back_url if body else None),
                    "price_estimate": price_info.get("estimate"),
                    "sources": price_info.get("results") or [],
                    "tags": tags,
                    "csv_exported": False,
                }
            ).execute()
        except Exception:
            pass

        # Feed card_context_index for Roshi recall
        try:
            snippet = None
            results = price_info.get("results") if isinstance(price_info, dict) else None
            if results:
                first = results[0] if isinstance(results, list) and results else None
                snippet = first.get("description") or first.get("title") if isinstance(first, dict) else None
            summary_parts = [
                card_name or "",
                series or "",
                f"card {card_number}" if card_number else "",
                f"rarity {rarity}" if rarity else "",
                f"value estimate ${price_info.get('estimate')}" if isinstance(price_info, dict) and price_info.get("estimate") else "",
            ]
            summary = ", ".join([p for p in summary_parts if p]).strip().strip(",")
            embed_res = embed_text(summary or card_name or "")
            vector = embed_res.get("vector") if isinstance(embed_res, dict) else None
            if vector:
                supabase.table("card_context_index").insert(
                    {
                        "card_id": record_id,
                        "embedding": vector,
                        "context_text": summary or snippet or card_name,
                        "image_url": storage.get("front") or (body.front_url if body else None),
                        "brave_snippet": snippet,
                        "ebay_link": price_info.get("source") if isinstance(price_info, dict) else None,
                        "card_name": card_name,
                        "card_number": card_number,
                        "series": series,
                        "value_estimate": price_info.get("estimate") if isinstance(price_info, dict) else None,
                    }
                ).execute()
        except Exception:
            pass

    return {
        "id": record_id,
        "card_name": card_name,
        "series": series,
        "card_number": card_number,
        "rarity": rarity,
        "price": price_info,
        "front_scan": front_scan,
        "back_scan": back_scan,
        "storage": storage,
        "source_bucket": CARD_BUCKET,
    }


def _to_bool(val):
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).lower() in {"true", "1", "yes", "on"}


@router.post("/tool/ocr")
async def ocr_tool_handler(payload: OcrToolRequest):
    data = await _fetch_file_bytes(payload.file_url)
    try:
        scan = stealth_ocr_engine.psycheract_scan(data, prefer_offline=payload.prefer_offline)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}")

    text = scan.get("text_extracted") or scan.get("raw_text") or ""
    response = {
        "text": text.strip(),
        "confidence": scan.get("confidence", 0),
        "method_used": scan.get("method_used"),
        "stealth_encoded": bool(scan.get("stealth_encoded") and payload.taonga_mode),
    }
    if payload.taonga_mode:
        response["protection_metadata"] = scan.get("protection_metadata")
        response["raw_text"] = scan.get("raw_text")
    log_event(
        "kitenga_tool_ocr",
        "OCR tool executed",
        source="ocr_tool",
        data={"taonga_mode": payload.taonga_mode, "method": scan.get("method_used")},
    )
    return response


@router.post("/tool/translate")
async def translate_tool_handler(payload: TranslateToolRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    translation = translate_text(text, payload.target_language, payload.context)
    log_event(
        "kitenga_tool_translate",
        "Translation tool executed",
        source="translate_tool",
        data={"target_language": payload.target_language},
    )
    return {
        "translation": translation,
        "target_language": payload.target_language,
        "source_text": text,
    }


@router.post("/ask")
async def ask_kitenga(request: KitengaAskRequest):
    """Relay Te Ao chat prompts to the configured OpenAI assistant using the Assistants API."""
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")
    assistant_id = _get_kitenga_assistant_id()
    if not assistant_id:
        raise HTTPException(status_code=500, detail="KITENGA_ASSISTANT_ID not configured.")
    prompt = (request.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    thread_id = request.thread_id
    try:
        if not thread_id:
            thread = await async_openai_client.beta.threads.create()
            thread_id = thread.id
        await async_openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        run = await async_openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        final_run, tool_history = await _poll_assistant_run(thread_id, run.id)
        latest = await _latest_assistant_message(thread_id)
        reply_text = _extract_message_text(latest) if latest else ""
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Kitenga assistant call failed: {exc}")

    session_id = request.session_id or "kitenga-te-ao"
    metadata = request.metadata if isinstance(request.metadata, dict) else {}
    try:
        log_chat_entry(
            session_id=session_id,
            thread_id=thread_id,
            user_message=prompt,
            assistant_reply=reply_text,
            mode="assistant",
            metadata={"route": "kitenga_ask", **metadata},
            tool_outputs=tool_history,
        )
    except Exception:
        pass

    return {
        "reply": reply_text,
        "thread_id": thread_id,
        "run_id": getattr(final_run, "id", None),
        "assistant_id": assistant_id,
        "tool_results": tool_history,
    }


@router.post("/gpt-whisper")
async def gpt_whisper(
    request: Request,
    payload: WhisperRequest | None = Body(default=None),
    file: UploadFile | None = File(default=None),
    whisper: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    session_id_q: str | None = Query(default=None),
    thread_id: str | None = Form(default=None),
    system_prompt: str | None = Form(default=None),
    run_pipeline: bool | str = Form(default=False),
    save_vector: bool | str = Form(default=False),
    use_retrieval: bool | str = Form(default=False),
    use_openai_summary: bool | str = Form(default=False),
    use_openai_translation: bool | str = Form(default=False),
    mode: str | None = Form(default="research"),
    allow_taonga_store: bool | str = Form(default=False),
    source: str | None = Form(default=None),
    authorization: str | None = Header(default=None),
):
    """Free-form text -> OpenAI response with optional retrieval/pipeline/vector persistence. Supports JSON or multipart/form-data with file."""
    _auth_check(authorization)
    if client is None:
        raise HTTPException(status_code=503, detail="OpenAI client not configured.")

    # If multipart/form-data provided, override payload
    if file is not None or whisper is not None:
        payload = WhisperRequest(
            whisper=whisper or "",
            session_id=session_id or session_id_q,
            thread_id=thread_id,
            system_prompt=system_prompt,
            run_pipeline=_to_bool(run_pipeline),
            save_vector=_to_bool(save_vector),
            use_retrieval=_to_bool(use_retrieval),
            use_openai_summary=_to_bool(use_openai_summary),
            use_openai_translation=_to_bool(use_openai_translation),
            mode=mode or "research",
            allow_taonga_store=_to_bool(allow_taonga_store),
            source=source,
        )
    # Fallback: attempt to parse JSON body manually when no file/form was sent
    elif payload is None:
        try:
            data = await request.json()
            if isinstance(data, dict):
                payload = WhisperRequest(**data)
        except Exception:
            payload = None

    if payload is None:
        raise HTTPException(status_code=400, detail="Missing payload.")

    mode = "response"
    thread_id: str | None = payload.thread_id
    pipeline_result = None
    vector_result = None
    summary_result = None
    translation_result = None
    session_id = payload.session_id or "anon"
    data_mode = payload.mode or "research"
    file_bytes: bytes | None = None
    file_name: str | None = None

    # If file present, read bytes
    if file is not None:
        file_bytes = await file.read()
        file_name = file.filename or "upload"

    # Retrieve prior chat context (long-term recall) for this session
    context_matches = []
    if payload.session_id:
        try:
            context_matches = retrieve_context(payload.whisper, session_id=session_id, top_k=5)
        except Exception:
            context_matches = []

    def _context_block():
        if not context_matches:
            return None
        lines = []
        for m in context_matches:
            role = m.get("role", "user")
            ts = m.get("ts", "")
            txt = (m.get("text") or "")[:400]
            lines.append(f"[{role} @ {ts}] {txt}")
        return "\n".join(lines)

    # Optional retrieval via Assistant + vector store
    if payload.use_retrieval and settings.openai_assistant_id_qa:
        try:
            if not thread_id:
                thread = client.beta.threads.create()
                thread_id = thread.id
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=payload.whisper,
            )
            instructions = payload.system_prompt or ""
            ctx = _context_block()
            if ctx:
                instructions = (instructions + "\n\nContext:\n" + ctx).strip()
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.openai_assistant_id_qa,
                instructions=instructions or None,
            )
            # Poll briefly for completion
            for _ in range(12):
                status_resp = client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )
                if status_resp.status in {"completed", "failed", "cancelled", "expired"}:
                    break
                time.sleep(0.5)
            if status_resp.status != "completed":
                raise HTTPException(
                    status_code=503,
                    detail=f"Assistant run not completed (status={status_resp.status})",
                )
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            reply = (
                messages.data[0].content[0].text.value
                if messages.data
                else "[no response]"
            )
            mode = "assistant"
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Assistant retrieval failed: {exc}")
    else:
        try:
            inputs: list[dict[str, str]] = []
            ctx_block = _context_block()
            
            # Add system prompt
            if payload.system_prompt:
                inputs.append({"role": "system", "content": payload.system_prompt})
            
            # Add project state context (live project snapshot)
            try:
                project_state = get_project_state()
                if project_state and "error" not in project_state:
                    state_context = format_project_state_for_context(project_state)
                    inputs.append({"role": "system", "content": state_context})
            except Exception:
                pass  # If project state unavailable, continue without it
            
            # Add chat history context
            if ctx_block:
                inputs.append({"role": "system", "content": f"Recent chat context:\n{ctx_block}"})
            
            inputs.append({"role": "user", "content": payload.whisper})
            reply = generate_text(inputs, model=DEFAULT_BACKEND_MODEL, max_tokens=2000)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")

    if payload.save_vector:
        vector_result = embed_text(
            payload.whisper,
            metadata={
                "session_id": session_id,
                "thread_id": thread_id,
                "role": "user",
                "mode": mode,
                "source": payload.source or data_mode or "whisper",
            },
            record_type="chat_embedding",
        )

    if payload.run_pipeline:
        data_bytes = file_bytes if file_bytes is not None else payload.whisper.encode("utf-8")
        fname = file_name or f"whisper_{uuid.uuid4().hex}.txt"
        pipeline_result = exec_pipeline(
            data_bytes,
            filename=fname,
            source=payload.source or data_mode or "whisper",
            generate_summary=payload.use_openai_summary,
            mode=data_mode,
            allow_taonga_store=payload.allow_taonga_store,
        )
        # Prefer pipeline-produced summary (short/long) if available
        if isinstance(pipeline_result, dict):
            if pipeline_result.get("summary_long"):
                summary_result = summary_result or pipeline_result.get("summary_long")
            elif pipeline_result.get("summary"):
                summary_result = summary_result or pipeline_result.get("summary")
            reply = summary_result or reply

    # Optional OpenAI summary/translation convenience
    try:
        if payload.use_openai_summary and not summary_result:
            summary_result = generate_text(
                [
                    {
                        "role": "system",
                        "content": (
                            "Summarize thoroughly. Return two sections:\n"
                            "1) Summary — 8-12 concise bullets covering key points, people, places, dates, and actions. "
                            "Scale up to cover long inputs fully.\n"
                            "2) Cultural notes — 3-5 bullets on Māori concepts, tikanga/taonga considerations, whakapapa references, "
                            "and any cautions or verification gaps.\n"
                        ),
                    },
                    {"role": "user", "content": payload.whisper},
                ],
                model=DEFAULT_BACKEND_MODEL,
                max_tokens=800,
            )
        if payload.use_openai_translation:
            translation_result = generate_text(
                [
                    {"role": "system", "content": "Translate the following text to te reo Māori, preserving meaning."},
                    {"role": "user", "content": payload.whisper},
                ],
                model=DEFAULT_BACKEND_MODEL,
                max_tokens=600,
            )
    except Exception:
        pass

    # Record chat turns to memory (user + assistant)
    try:
        record_turn(
            session_id=session_id,
            thread_id=thread_id,
            role="user",
            text=payload.whisper,
            mode=mode,
            source=payload.source or "whisper",
        )
        record_turn(
            session_id=session_id,
            thread_id=thread_id,
            role="assistant",
            text=reply,
            mode=mode,
            source=payload.source or "whisper",
        )
    except Exception:
        pass

    # Best-effort chat log to Supabase
    try:
        log_chat_entry(
            session_id=session_id,
            thread_id=thread_id,
            user_message=payload.whisper,
            assistant_reply=reply,
            mode=mode,
            vector_batch_id=pipeline_result.get("vector_batch_id") if isinstance(pipeline_result, dict) else None,
            pipeline_result=pipeline_result if isinstance(pipeline_result, dict) else None,
            metadata={
                "use_retrieval": payload.use_retrieval,
                "save_vector": payload.save_vector,
                "run_pipeline": payload.run_pipeline,
                "source": payload.source or data_mode or "whisper",
                "data_mode": data_mode,
                "use_openai_summary": payload.use_openai_summary,
                "use_openai_translation": payload.use_openai_translation,
            },
        )
    except Exception:
        pass

    log_event(
        "gpt_whisper",
        "Whisper processed",
        source=payload.source or "whisper",
        data={
            "mode": mode,
            "session_id": payload.session_id,
            "thread_id": thread_id,
            "use_retrieval": payload.use_retrieval,
            "save_vector": payload.save_vector,
            "run_pipeline": payload.run_pipeline,
            "pipeline": pipeline_result,
            "vector": vector_result,
            "summary": summary_result,
            "translation": translation_result,
        },
    )

    return {
        "response": reply,
        "mode": mode,
        "thread_id": thread_id,
        "pipeline": pipeline_result,
        "vector": vector_result,
        "summary": summary_result,
        "translation": translation_result,
    }


# Define the vector_search tool
def vector_search_tool():
    return Tool(
        name="vector_search",
        description="Search vector memory for relevant context.",
        execute=lambda params: {
            "status": "success",
            "results": "Vector search results for params: {}".format(params)
        },
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "top_k": {"type": "integer", "description": "Number of top results to return.", "default": 5},
                "threshold": {"type": "number", "description": "Minimum similarity threshold.", "default": 0.7}
            },
            "required": ["query"]
        }
    )

# Register the tool
vector_search = vector_search_tool()

@router.post("/run_pipeline")
async def run_pipeline_endpoint(
    pipeline_name: str = Form(...),
    input_data: str = Form(...),
    realm_name: str = Form(default="Te_Po"),
    verbose: bool = Form(default=False)
):
    """
    Endpoint to execute a pipeline.
    Args:
        pipeline_name: Name of the pipeline to execute.
        input_data: Input data for the pipeline.
        realm_name: Realm in which the pipeline resides.
        verbose: Whether to show detailed logs.
    Returns:
        Pipeline execution results.
    """
    try:
        result = run_pipeline(realm_name, pipeline_name, input_data, verbose)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/query_knowledge_base")
async def query_knowledge_base(
    query: str = Form(...),
    top_k: int = Form(default=5),
    min_similarity: float = Form(default=0.7)
):
    """
    Endpoint to query the knowledge base using vector search.
    Args:
        query: The search query string.
        top_k: Number of top results to return.
        min_similarity: Minimum similarity threshold for results.
    Returns:
        A list of matching knowledge base entries.
    """
    try:
        results = search_text(query=query, top_k=top_k, min_similarity=min_similarity)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}
