from datetime import datetime
import platform
import requests

from fastapi import APIRouter
from te_po.core.config import settings
from te_po.utils.openai_client import client
from te_po.utils.supabase_client import get_client
import socket

router = APIRouter(tags=["Status"])


@router.get("/status")
async def status():
    """Lightweight health endpoint for Te Pō."""
    return {
        "realm": "te_po",
        "status": "online",
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": platform.node(),
    }


@router.get("/status/openai")
async def status_openai():
    """Check OpenAI readiness (key present, optional vector store reachable)."""
    ready = client is not None and bool(settings.openai_api_key)
    vector_ok = None
    vector_reason = None
    if ready and settings.openai_vector_store_id:
        try:
            # New OpenAI client exposes vector stores under client.beta.vector_stores
            resp = client.beta.vector_stores.retrieve(settings.openai_vector_store_id)
            vector_ok = True
            vector_reason = getattr(resp, "status", "ok")
        except Exception as exc:
            vector_ok = False
            vector_reason = str(exc)
    return {
        "openai_ready": ready,
        "vector_store_id": settings.openai_vector_store_id,
        "vector_ok": vector_ok,
        "vector_reason": vector_reason,
    }


@router.get("/status/full")
async def status_full():
    supa = get_client()
    supabase_ok = supa is not None
    supabase_reason = None
    try:
        if supa:
            supa.table("kitenga_artifacts").select("id").limit(1).execute()
    except Exception as exc:
        supabase_ok = False
        supabase_reason = str(exc)

    openai_ok = client is not None and bool(settings.openai_api_key)
    vector_ok = None
    try:
        if openai_ok and settings.openai_vector_store_id:
            resp = client.beta.vector_stores.retrieve(settings.openai_vector_store_id)
            vector_ok = getattr(resp, "status", "ok")
    except Exception as exc:
        vector_ok = str(exc)

    ollama_ok = False
    if settings.ollama_base_url:
        try:
            resp = requests.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=5)
            resp.raise_for_status()
            ollama_ok = True
        except Exception:
            ollama_ok = False

    return {
        "realm": "te_po",
        "status": "online",
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": platform.node(),
        "api_host": socket.gethostname(),
        "openai_ok": openai_ok,
        "vector_status": vector_ok,
        "supabase_ok": supabase_ok,
        "supabase_reason": supabase_reason,
        "ollama_ok": ollama_ok,
        "ollama_model": settings.ollama_model,
    }
