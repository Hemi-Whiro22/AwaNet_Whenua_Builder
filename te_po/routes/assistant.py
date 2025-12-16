import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from openai import OpenAI
from fastapi import APIRouter, Body, Header, HTTPException, status

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.utils.audit import log_event

router = APIRouter(prefix="/assistant", tags=["Assistant"])
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID") or os.getenv("KITENGA_ASSISTANT_ID")
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_DIR = Path("te_po/storage/logs/assistant_calls")


def _auth_check(authorization: Optional[str]):
    if PIPELINE_TOKEN:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
        token = authorization.split(" ", 1)[1].strip()
        if token != PIPELINE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token.")


def _log_assistant_call(payload: dict, result: dict, source: str):
    log_data = {
        "input": payload,
        "result": result,
        "assistant_id": ASSISTANT_ID,
        "vector_store_id": VECTOR_STORE_ID,
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOG_DIR / f"{source}_response.json"
        log_path.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
    except Exception:
        # Best-effort logging; avoid impacting the endpoint.
        return


@router.post("/run")
async def assistant_run(
    payload: dict = Body(...),
    authorization: str | None = Header(default=None),
):
    """
    Bridge endpoint for assistant tool-calls.
    Accepts either:
    - file_url: URL to fetch file bytes
    - text: inline text to process
    """
    _auth_check(authorization)

    file_url = payload.get("file_url")
    text = payload.get("text")
    source = payload.get("source", "assistant")

    if not file_url and not text:
        raise HTTPException(status_code=400, detail="Provide file_url or text.")

    data: bytes
    filename: str

    if file_url:
        try:
            resp = httpx.get(file_url, timeout=30)
            resp.raise_for_status()
            data = resp.content
            filename = file_url.split("/")[-1] or "assistant_file"
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to fetch file_url: {exc}")
    else:
        data = (text or "").encode("utf-8")
        filename = "assistant_inline.txt"

    result = run_pipeline(data, filename, source=source)
    _log_assistant_call(payload, result, source)
    log_event(
        "assistant_run",
        "Assistant bridge executed",
        source=source,
        data={"input_kind": "file_url" if file_url else "text", "result": result},
    )
    return result


@router.post("/create")
async def create_assistant(
    payload: dict = Body(...),
    authorization: str | None = Header(default=None),
):
    """
    Create an OpenAI Assistant with optional vector store.
    Used by Realm Generator to spin up kaitiaki with their own vector stores.
    
    Payload:
    - name: Assistant name (required)
    - instructions: System instructions (required)
    - model: Model to use (default: gpt-4o)
    - create_vector_store: Whether to create a vector store (default: True)
    - vector_store_name: Name for the vector store
    """
    _auth_check(authorization)
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    name = payload.get("name")
    instructions = payload.get("instructions")
    model = payload.get("model", "gpt-4o")
    create_vs = payload.get("create_vector_store", True)
    vs_name = payload.get("vector_store_name", f"{name}_vector_store" if name else "new_vector_store")
    
    if not name or not instructions:
        raise HTTPException(status_code=400, detail="name and instructions are required")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        vector_store_id = None
        
        # Create vector store if requested
        if create_vs:
            vs = client.vector_stores.create(name=vs_name)
            vector_store_id = vs.id
        
        # Create assistant with file_search tool
        tools = [{"type": "file_search"}] if create_vs else []
        tool_resources = {}
        if vector_store_id:
            tool_resources = {"file_search": {"vector_store_ids": [vector_store_id]}}
        
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools,
            tool_resources=tool_resources if tool_resources else None,
        )
        
        result = {
            "assistant_id": assistant.id,
            "assistant_name": assistant.name,
            "model": assistant.model,
            "vector_store_id": vector_store_id,
            "vector_store_name": vs_name if vector_store_id else None,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        
        # Log to kitenga schema
        try:
            from te_po.db.kitenga_db import log_whakapapa, log_event as db_log
            log_whakapapa(
                id=f"assistant-{assistant.id}",
                title=f"Assistant: {name}",
                category="assistant_creation",
                summary=f"Created OpenAI assistant {name} with vector store {vector_store_id}",
                content_type="assistant",
                data=result,
                author="kitenga_whiro"
            )
            db_log("assistant_created", f"Created assistant {name}", "assistant_route", result)
        except Exception:
            pass  # Non-critical logging
        
        return result
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create assistant: {exc}")


@router.get("/list")
async def list_assistants(
    authorization: str | None = Header(default=None),
    limit: int = 20,
):
    """List all OpenAI assistants."""
    _auth_check(authorization)
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        assistants = client.beta.assistants.list(limit=limit)
        
        return {
            "assistants": [
                {
                    "id": a.id,
                    "name": a.name,
                    "model": a.model,
                    "created_at": a.created_at,
                }
                for a in assistants.data
            ],
            "count": len(assistants.data)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list assistants: {exc}")


@router.get("/vector-stores")
async def list_vector_stores(
    authorization: str | None = Header(default=None),
    limit: int = 20,
):
    """List all OpenAI vector stores."""
    _auth_check(authorization)
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        stores = client.vector_stores.list(limit=limit)
        
        return {
            "vector_stores": [
                {
                    "id": s.id,
                    "name": s.name,
                    "file_counts": s.file_counts,
                    "created_at": s.created_at,
                    "status": s.status,
                }
                for s in stores.data
            ],
            "count": len(stores.data)
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list vector stores: {exc}")