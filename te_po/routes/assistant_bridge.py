"""
Kitenga Whiro Assistant Bridge
Connects Te Pō backend to OpenAI Assistant (asst_WvuWFEv2FpNWwEn11gbvSbHA)
and vector store (vs_692ee26573688191817773029871850d).
Handles retries, logging, and health diagnostics.
"""

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/assistant", tags=["assistant"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("KITENGA_ASSISTANT_ID")
VECTOR_ID = os.getenv("KITENGA_VECTOR_STORE_ID")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "assistant_bridge.log"
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def _call_openai(data: dict[str, Any], retries: int = 3, delay: int = 2):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    for attempt in range(1, retries + 1):
        res = requests.post(f"{BASE_URL}/assistants/runs", json=data, headers=headers)
        if res.status_code == 200:
            return res.json()
        logging.warning(f"Attempt {attempt} failed ({res.status_code}): {res.text[:200]}")
        time.sleep(delay)

    raise HTTPException(status_code=502, detail="Failed to reach OpenAI after retries")


@router.post("/run")
def run_assistant(payload: dict[str, Any]):
    text = payload.get("text")
    thread_id = payload.get("thread_id")

    if not text:
        raise HTTPException(status_code=400, detail="Missing `text` in payload")

    data = {
        "assistant_id": ASSISTANT_ID,
        "model": "gpt-4o",
        "input": text,
        "thread": {"id": thread_id} if thread_id else {},
        "tools": [{"type": "file_search", "vector_store_ids": [VECTOR_ID]}],
    }
    result = _call_openai(data)
    logging.info(f"Assistant run: {text[:60]}... -> {result.get('id', 'no-id')}")
    return result


@router.get("/health")
def health_check():
    return {
        "assistant_id": ASSISTANT_ID,
        "vector_id": VECTOR_ID,
        "openai_key": "set" if OPENAI_API_KEY else "missing",
        "status": "ok",
    }


@router.get("/version")
def version():
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError:
        commit = "unknown"
    return {
        "commit": commit,
        "assistant_id": ASSISTANT_ID,
        "vector_id": VECTOR_ID,
        "openai_key": "set" if OPENAI_API_KEY else "missing",
    }
