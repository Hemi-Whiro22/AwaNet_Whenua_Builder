import json
import uuid

from te_po.services.local_storage import save, timestamp
from te_po.utils.openai_client import client, generate_text


def summarize_text(text: str, mode: str = "research"):
    if client is None:
        return {"id": None, "summary": "[offline] OpenAI client not configured.", "mode": mode, "saved": False}
    try:
        style = "deep academic analysis" if mode == "research" else "taonga-aligned cultural summary"
        out = generate_text(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Summarize with {style}. "
                        "Return two sections:\n"
                        "1) Summary — 8-12 concise bullets covering all key points, people, places, dates, and actions.\n"
                        "2) Cultural notes — 3-5 bullets on Māori concepts, tikanga/taonga considerations, whakapapa references, and any cautions or gaps to verify.\n"
                        "If the text is long, extend to ensure coverage; be clear and specific."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        entry_id = f"summary_{uuid.uuid4().hex}"
        save(
            "openai",
            f"{entry_id}.json",
            json.dumps(
                {"id": entry_id, "mode": mode, "input": text, "output": out, "ts": timestamp()},
                indent=2,
            ),
        )
        return {"id": entry_id, "summary": out, "mode": mode, "saved": True}
    except Exception as exc:
        return {"id": None, "summary": f"Summary failed: {exc}", "mode": mode, "saved": False}
