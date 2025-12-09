"""Simplified OpenAI client helpers for local-only mode."""

from __future__ import annotations

import asyncio
import os
from typing import Sequence

from openai import OpenAI

from te_po.core.config import settings

DEFAULT_BACKEND_MODEL = settings.backend_model or os.environ.get(
    "OPENAI_BACKEND_MODEL", "gpt-5.1"
)
DEFAULT_TRANSLATION_MODEL = settings.translation_model or os.environ.get(
    "OPENAI_TRANSLATION_MODEL", "gpt-4o-mini"
)
DEFAULT_VISION_MODEL = settings.vision_model or os.environ.get(
    "OPENAI_VISION_MODEL", "gpt-4o-mini"
)
DEFAULT_UI_MODEL = settings.ui_model or os.environ.get("OPENAI_UI_MODEL", "gpt-4o")
DEFAULT_EMBED_MODEL = settings.embedding_model or os.environ.get(
    "OPENAI_EMBED_MODEL", "text-embedding-3-large"
)

try:
    client = OpenAI()
except Exception:
    client = None


async def call_openai(prompt: str, model: str | None = None) -> str:
    """Async wrapper to call OpenAI responses API with a simple system prompt."""
    if client is None:
        return "[offline] OpenAI API key missing."
    use_model = model or DEFAULT_BACKEND_MODEL

    def _call():
        response = client.responses.create(
            model=use_model,
            input=[
                {"role": "system", "content": "You are a precise Māori reo assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text.strip()

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call)


def translate_text(
    text: str,
    target_language: str,
    context: str | None = None,
    model: str | None = None,
) -> str:
    if client is None:
        return f"[{target_language}] {text}"
    system_message = (
        f"Translate the user's text into {target_language} while preserving nuance and macrons."
    )
    if context:
        system_message += f" Context: {context.strip()}"
    response = client.responses.create(
        model=model or DEFAULT_TRANSLATION_MODEL,
        input=[
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": text},
        ],
    )
    return response.output_text.strip()


def generate_embedding(text: str) -> Sequence[float]:
    if client is None:
        # Deterministic pseudo embedding fallback
        return [float((idx % 7) / 10) for idx in range(32)]
    response = client.embeddings.create(
        model=DEFAULT_EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def generate_text(messages: list[dict], model: str | None = None, max_tokens: int = 500) -> str:
    """
    Create text with either the Responses API (if available) or fallback to chat.completions.
    """
    if client is None:
        raise RuntimeError("OpenAI client not configured.")
    use_model = model or DEFAULT_BACKEND_MODEL
    if hasattr(client, "responses"):
        resp = client.responses.create(
            model=use_model,
            input=messages,
            max_output_tokens=max_tokens,
        )
        return (resp.output_text or "").strip()
    if not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
        raise RuntimeError("OpenAI client missing responses and chat.completions APIs.")
    chat_messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
    # Prefer new parameter name for newer models; fallback to legacy if rejected.
    last_exc = None
    for token_param in (
        {"max_output_tokens": max_tokens},
        {"max_completion_tokens": max_tokens},
        {"max_tokens": max_tokens},
    ):
        try:
            resp = client.chat.completions.create(
                model=use_model,
                messages=chat_messages,
                **token_param,
            )
            break
        except Exception as exc:
            last_exc = exc
            resp = None
    if resp is None:
        raise last_exc or RuntimeError("chat.completions call failed.")
    choice = resp.choices[0] if getattr(resp, "choices", None) else None
    return (choice.message.content or "").strip() if choice else ""
