"""
Tool implementations for Whiro (Te Pō MCP).

These tools proxy Te Pō HTTP endpoints. They avoid importing the FastAPI app to
keep tooling decoupled from runtime.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _base_url() -> str:
    return os.getenv("TE_PO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _headers() -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    token = os.getenv("PIPELINE_TOKEN") or os.getenv("HUMAN_BEARER_KEY")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_status() -> Dict[str, Any]:
    resp = requests.get(f"{_base_url()}/heartbeat", headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def run_pipeline_from_text(text: str, source: str = "whiro_tool") -> Dict[str, Any]:
    payload = {"text": text, "source": source}
    resp = requests.post(
        f"{_base_url()}/pipeline/run",
        headers=_headers(),
        files=None,
        data=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def kitenga_ask(prompt: str) -> Dict[str, Any]:
    payload = {"prompt": prompt}
    resp = requests.post(
        f"{_base_url()}/kitenga/ask",
        headers=_headers(),
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()
