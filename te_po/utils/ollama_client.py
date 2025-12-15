from __future__ import annotations

from typing import List, Dict, Optional

import requests

from te_po.core.config import settings


def _base_url() -> str:
    return settings.ollama_base_url.rstrip("/")


def chat_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    options: Optional[Dict] = None,
    stream: bool = False,
) -> Dict:
    """Low-level helper to call Ollama's /api/chat endpoint."""
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": stream,
    }
    if options:
        payload["options"] = options
    resp = requests.post(
        f"{_base_url()}/api/chat",
        json=payload,
        timeout=settings.ollama_timeout,
    )
    resp.raise_for_status()
    return resp.json()


def generate_llama_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """Convenience wrapper that returns a string response from Llama."""
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    data = chat_ollama(messages=messages, model=model)
    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        # fallback to entire response for debugging
        content = str(data)
    return content.strip()
