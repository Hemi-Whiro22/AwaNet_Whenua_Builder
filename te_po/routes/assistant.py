import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Body, Header, HTTPException, status

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

router = APIRouter(prefix="/assistant", tags=["Assistant"])
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID") or os.getenv("KITENGA_ASSISTANT_ID")
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")
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
    return result
