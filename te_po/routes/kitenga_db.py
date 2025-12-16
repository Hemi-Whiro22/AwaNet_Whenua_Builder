"""
Kitenga Schema API Routes
Exposes the kitenga schema database to the API.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from te_po.db.kitenga_db import (
    # Logs
    log_event, get_recent_logs,
    # Memory
    store_memory, search_memory, log_memory_event,
    # Chat
    save_chat_log, get_chat_history,
    # Taonga
    store_taonga, search_taonga, get_taonga_by_id,
    # OCR
    save_ocr_log,
    # Pipeline
    create_pipeline_run, update_pipeline_run, get_recent_pipeline_runs,
    # Artifacts
    store_artifact,
    # Whakapapa
    log_whakapapa,
    # Stats
    get_schema_stats, test_connection
)

router = APIRouter(prefix="/kitenga/db", tags=["Kitenga Schema"])


# ==================== MODELS ====================

class LogEventRequest(BaseModel):
    event: str
    detail: str
    source: str = "kitenga_whiro"
    data: Optional[Dict[str, Any]] = None


class MemoryRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatLogRequest(BaseModel):
    session_id: str
    user_message: str
    assistant_reply: str
    thread_id: Optional[str] = None
    mode: str = "chat"
    metadata: Optional[Dict[str, Any]] = None


class TaongaRequest(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class WhakapapaRequest(BaseModel):
    id: str
    title: str
    category: str
    summary: str
    content_type: str = "event"
    data: Optional[Dict[str, Any]] = None
    author: str = "kitenga_whiro"


# ==================== ROUTES ====================

@router.get("/status")
async def kitenga_db_status():
    """Check kitenga schema connection status."""
    return test_connection()


@router.get("/stats")
async def kitenga_db_stats():
    """Get kitenga schema statistics."""
    return get_schema_stats()


# --- Logs ---

@router.post("/logs")
async def create_log(req: LogEventRequest):
    """Create a log entry in kitenga.logs."""
    log_id = log_event(req.event, req.detail, req.source, req.data)
    return {"id": log_id, "status": "logged"}


@router.get("/logs/recent")
async def recent_logs(limit: int = 50, source: str = None):
    """Get recent log entries."""
    logs = get_recent_logs(limit, source)
    return {"logs": logs, "count": len(logs)}


# --- Memory ---

@router.post("/memory")
async def create_memory(req: MemoryRequest):
    """Store context memory."""
    mem_id = store_memory(req.content, req.metadata)
    return {"id": mem_id, "status": "stored"}


@router.post("/memory/search")
async def search_memory_route(req: SearchRequest):
    """Search context memory."""
    results = search_memory(req.query, req.limit)
    return {"results": results, "count": len(results)}


# --- Chat ---

@router.post("/chat/log")
async def create_chat_log(req: ChatLogRequest):
    """Save a chat log entry."""
    log_id = save_chat_log(
        req.session_id, req.user_message, req.assistant_reply,
        req.thread_id, req.mode, req.metadata
    )
    return {"id": log_id, "status": "saved"}


@router.get("/chat/history/{session_id}")
async def chat_history(session_id: str, limit: int = 50):
    """Get chat history for a session."""
    history = get_chat_history(session_id, limit)
    return {"history": history, "count": len(history)}


# --- Taonga ---

@router.post("/taonga")
async def create_taonga(req: TaongaRequest):
    """Store a taonga."""
    taonga_id = store_taonga(req.title, req.content, req.metadata)
    return {"id": taonga_id, "status": "stored"}


@router.get("/taonga/{taonga_id}")
async def get_taonga(taonga_id: str):
    """Get a taonga by ID."""
    taonga = get_taonga_by_id(taonga_id)
    if not taonga:
        raise HTTPException(status_code=404, detail="Taonga not found")
    return taonga


@router.post("/taonga/search")
async def search_taonga_route(req: SearchRequest):
    """Search taonga."""
    results = search_taonga(req.query, req.limit)
    return {"results": results, "count": len(results)}


# --- Pipeline ---

@router.get("/pipeline/recent")
async def recent_pipelines(limit: int = 20):
    """Get recent pipeline runs."""
    runs = get_recent_pipeline_runs(limit)
    return {"runs": runs, "count": len(runs)}


# --- Whakapapa ---

@router.post("/whakapapa")
async def create_whakapapa(req: WhakapapaRequest):
    """Log to whakapapa (lineage)."""
    whakapapa_id = log_whakapapa(
        req.id, req.title, req.category, req.summary,
        req.content_type, req.data, req.author
    )
    return {"id": whakapapa_id, "status": "logged"}
