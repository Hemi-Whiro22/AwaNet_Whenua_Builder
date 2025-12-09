import json
import uuid

from te_po.services.local_storage import save, timestamp
from te_po.utils.openai_client import (
    client,
    DEFAULT_BACKEND_MODEL,
    DEFAULT_TRANSLATION_MODEL,
    generate_text,
)


def _build_entry(text: str, output: str, kind: str):
    entry_id = f"reo_{uuid.uuid4().hex}"
    payload = {"id": entry_id, "input": text, "output": output, "ts": timestamp(), "type": kind}
    save("logs", f"{entry_id}.json", json.dumps(payload, indent=2))
    return {"id": entry_id, "output": output, "type": kind, "saved": True}


def _offline(kind: str, message: str):
    return {"id": None, "output": message, "type": kind, "saved": False}


def translate_reo(text: str):
    if client is None:
        return _offline("translate", "[offline] OpenAI client not configured.")
    try:
        out = generate_text(
            model=DEFAULT_TRANSLATION_MODEL,
            messages=[
                {"role": "system", "content": "Translate into te reo Māori with correct dialect + grammar."},
                {"role": "user", "content": text},
            ],
        )
        return _build_entry(text, out, "translate")
    except Exception as exc:
        return _offline("translate", f"Reo translate failed: {exc}")


def explain_reo(text: str):
    if client is None:
        return _offline("explain", "[offline] OpenAI client not configured.")
    try:
        out = generate_text(
            model=DEFAULT_BACKEND_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Explain Māori kupu with gentle teaching tone. Include cultural context when relevant.",
                },
                {"role": "user", "content": text},
            ],
        )
        return _build_entry(text, out, "explain")
    except Exception as exc:
        return _offline("explain", f"Reo explain failed: {exc}")


def pronounce_reo(text: str):
    if client is None:
        return _offline("pronounce", "[offline] OpenAI client not configured.")
    try:
        out = generate_text(
            model=DEFAULT_BACKEND_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Provide phonetic pronunciation guidance for te reo Māori kupu using double-vowel notation. "
                        "Add short tips if kupu has dialectal variations."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        return _build_entry(text, out, "pronounce")
    except Exception as exc:
        return _offline("pronounce", f"Reo pronounce failed: {exc}")
