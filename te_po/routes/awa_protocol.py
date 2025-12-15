"""
Te Pō /awa/* Routes
Model Context Protocol integration routes for direct MCP access.
These routes power the Te Pō MCP server.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

router = APIRouter(prefix="/awa", tags=["awa-protocol"])
logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class EnvelopeRequest(BaseModel):
    """Wrap message with realm context."""
    message: str
    realm: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    """Execute a kaitiaki task."""
    kaitiaki: str
    task: str
    input: Dict[str, Any]
    priority: str = "normal"
    realm: Optional[str] = None


class HandoffRequest(BaseModel):
    """Transfer task between kaitiaki."""
    from_kaitiaki: str
    to_kaitiaki: str
    task_id: str
    context: Optional[Dict[str, Any]] = None


class MemoryQueryRequest(BaseModel):
    """Query vector memory."""
    query: str
    top_k: int = 5
    threshold: float = 0.7
    realm: Optional[str] = None
    tapu_level: Optional[int] = None


class MemoryStoreRequest(BaseModel):
    """Store to vector memory."""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    realm: Optional[str] = None
    tapu_level: int = 0


class LogRequest(BaseModel):
    """Log activity."""
    event_type: str
    details: Dict[str, Any]
    realm: Optional[str] = None
    severity: str = "info"


class NotifyRequest(BaseModel):
    """Send notification."""
    recipient: str
    message: str
    channel: str = "default"
    priority: str = "normal"


class KaitiakiregisterRequest(BaseModel):
    """Register kaitiaki."""
    name: str
    role: str
    system_prompt: str
    tools: Optional[List[str]] = None
    realm: Optional[str] = None


class KaitiakiregisterResponse(BaseModel):
    """Kaitiaki registration response."""
    id: str
    name: str
    role: str
    created_at: str
    realm: Optional[str] = None


class VectorEmbedRequest(BaseModel):
    """Generate embeddings."""
    text: str
    model: Optional[str] = None


class VectorSearchResponse(BaseModel):
    """Search response."""
    results: List[Dict[str, Any]]
    count: int
    query: str


class PipelineRequest(BaseModel):
    """Run pipeline."""
    name: str
    input: Dict[str, Any]
    wait: bool = False
    realm: Optional[str] = None


# ============================================================================
# ROUTES: Envelope & Context
# ============================================================================

@router.post("/envelope")
async def wrap_envelope(req: EnvelopeRequest):
    """
    Wrap message with realm context.
    Adds realm identity, timestamp, and metadata.
    """
    try:
        response = {
            "original_message": req.message,
            "realm": req.realm or "global",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": req.metadata or {},
            "wrapped": True
        }
        logger.info(f"Envelope wrapped for realm: {req.realm}")
        return response
    except Exception as e:
        logger.error(f"Envelope wrap failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ROUTES: Task Execution
# ============================================================================

@router.post("/task")
async def execute_task(req: TaskRequest):
    """
    Execute a kaitiaki task.
    Routes to the specified kaitiaki with task details.
    """
    try:
        # Validate kaitiaki exists
        # TODO: Check kaitiaki registry

        logger.info(
            f"Task '{req.task}' assigned to {req.kaitiaki} (priority: {req.priority})")

        # TODO: Route to kaitiaki execution engine

        return {
            "task_id": f"task_{datetime.utcnow().timestamp()}",
            "kaitiaki": req.kaitiaki,
            "task": req.task,
            "status": "queued",
            "priority": req.priority,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/handoff")
async def handoff_task(req: HandoffRequest):
    """
    Transfer task between kaitiaki.
    Records context transfer and updates ownership.
    """
    try:
        logger.info(
            f"Task {req.task_id} transferred from {req.from_kaitiaki} to {req.to_kaitiaki}")

        return {
            "task_id": req.task_id,
            "from_kaitiaki": req.from_kaitiaki,
            "to_kaitiaki": req.to_kaitiaki,
            "status": "transferred",
            "context": req.context,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Handoff failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ROUTES: Vector Memory
# ============================================================================

@router.post("/memory/query")
async def query_memory(req: MemoryQueryRequest):
    """
    Semantic search across vector memory.
    Returns documents with similarity scores.
    """
    try:
        # TODO: Call vector search service
        # Example return:
        results = [
            {
                "id": "doc_123",
                "content": "Kaitiaki are guardians...",
                "similarity": 0.95,
                "metadata": {"source": "glossary"},
                "realm": req.realm
            }
        ]

        logger.info(
            f"Memory query: '{req.query[:50]}...' returned {len(results)} results")

        return {
            "query": req.query,
            "results": results,
            "count": len(results),
            "threshold": req.threshold
        }
    except Exception as e:
        logger.error(f"Memory query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/store")
async def store_memory(req: MemoryStoreRequest):
    """
    Store content to vector memory with embedding.
    Assigns tapu level and metadata.
    """
    try:
        # TODO: Generate embedding and store
        doc_id = f"doc_{datetime.utcnow().timestamp()}"

        logger.info(
            f"Stored to memory: {doc_id} (tapu_level: {req.tapu_level})")

        return {
            "id": doc_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "tapu_level": req.tapu_level,
            "metadata": req.metadata,
            "realm": req.realm,
            "status": "stored"
        }
    except Exception as e:
        logger.error(f"Memory store failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ROUTES: Logging & Notifications
# ============================================================================

@router.post("/log")
async def log_activity(req: LogRequest):
    """
    Log activity to carving log.
    Creates immutable audit trail entry.
    """
    try:
        # TODO: Append to mauri/state/*_carving_log.jsonl
        log_entry = {
            "timestamp": req.metadata.get("timestamp") if req.metadata else datetime.utcnow().isoformat() + "Z",
            "event_type": req.event_type,
            "details": req.details,
            "realm": req.realm,
            "severity": req.severity,
            "guardian": "haiku"  # Logged by Copilot/Haiku
        }

        logger.info(
            f"Activity logged: {req.event_type} (severity: {req.severity})")

        return {
            "logged": True,
            "entry": log_entry
        }
    except Exception as e:
        logger.error(f"Logging failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/notify")
async def send_notification(req: NotifyRequest):
    """
    Send notification to recipient.
    Supports multiple channels (Slack, email, realtime).
    """
    try:
        # TODO: Route to notification service
        logger.info(
            f"Notification sent to {req.recipient} via {req.channel} (priority: {req.priority})")

        return {
            "recipient": req.recipient,
            "channel": req.channel,
            "priority": req.priority,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ROUTES: Kaitiaki Management
# ============================================================================

@router.post("/kaitiaki/register")
async def register_kaitiaki(req: KaitiakiregisterRequest):
    """
    Register a new kaitiaki (guardian agent).
    Stores role, system prompt, and tool definitions.
    """
    try:
        kaitiaki_id = f"kaitiaki_{req.name.lower()}"

        logger.info(f"Kaitiaki registered: {req.name} (role: {req.role})")

        return KaitiakiregisterResponse(
            id=kaitiaki_id,
            name=req.name,
            role=req.role,
            created_at=datetime.utcnow().isoformat() + "Z",
            realm=req.realm
        )
    except Exception as e:
        logger.error(f"Kaitiaki registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/kaitiaki/context")
async def get_kaitiaki_context(kaitiaki: str, realm: Optional[str] = None):
    """
    Get context (state, capabilities, memory) for a kaitiaki.
    """
    try:
        # TODO: Fetch from kaitiaki registry + state
        context = {
            "kaitiaki": kaitiaki,
            "realm": realm,
            "status": "active",
            "capabilities": ["vector_search", "memory_store", "task_execute"],
            "memory_size": 1024,
            "active_tasks": 0,
            "last_activity": datetime.utcnow().isoformat() + "Z"
        }

        logger.info(f"Context retrieved for kaitiaki: {kaitiaki}")
        return context
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kaitiaki")
async def list_kaitiaki():
    """
    List all registered kaitiaki in the system.
    """
    try:
        kaitiaki_list = [
            {"name": "kitenga_whiro", "role": "Root navigator"},
            {"name": "ruru", "role": "OCR specialist"},
            {"name": "awanui", "role": "Translator"},
            {"name": "mataroa", "role": "Research/summary"},
            {"name": "te_puna", "role": "Knowledge portal"}
        ]

        logger.info(f"Listed {len(kaitiaki_list)} kaitiaki")
        return {"kaitiaki": kaitiaki_list, "count": len(kaitiaki_list)}
    except Exception as e:
        logger.error(f"Kaitiaki listing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ROUTES: Vector Operations
# ============================================================================

@router.post("/vector/embed")
async def generate_embeddings(req: VectorEmbedRequest):
    """
    Generate embeddings for text.
    Uses configured embedding model (OpenAI).
    """
    try:
        # TODO: Call embedding service
        logger.info(f"Generated embedding for text ({len(req.text)} chars)")

        return {
            "embedding": [0.0] * 1536,  # Placeholder
            "model": req.model or "text-embedding-3-small",
            "dimension": 1536,
            "tokens_used": len(req.text.split())
        }
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/vector/search")
async def semantic_search(req: MemoryQueryRequest):
    """Semantic search (alias for /awa/memory/query)."""
    return await query_memory(req)


# ============================================================================
# ROUTES: Pipelines
# ============================================================================

@router.post("/pipeline")
async def run_pipeline(req: PipelineRequest):
    """
    Execute a Te Pō pipeline.
    Valid pipelines: ocr, summarise, translate, embed, taonga
    """
    try:
        valid_pipelines = ["ocr", "summarise", "translate", "embed", "taonga"]
        if req.name not in valid_pipelines:
            raise ValueError(f"Unknown pipeline: {req.name}")

        logger.info(f"Pipeline '{req.name}' started (wait: {req.wait})")

        return {
            "pipeline": req.name,
            "status": "running" if not req.wait else "completed",
            "input": req.input,
            "realm": req.realm,
            "started_at": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pipelines")
async def list_pipelines():
    """List available pipelines."""
    pipelines = {
        "ocr": "Extract text from images/PDFs",
        "summarise": "Generate document summary",
        "translate": "Translate with dialect support",
        "embed": "Generate text embeddings",
        "taonga": "Classify and protect taonga (sacred content)"
    }
    return pipelines
