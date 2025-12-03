import json
import uuid

from te_po.services.local_storage import save, timestamp
from te_po.utils.openai_client import client


def summarize_text(text: str, mode: str = "research"):
    if client is None:
        return {"id": None, "summary": "[offline] OpenAI client not configured.", "mode": mode, "saved": False}
    try:
        style = "deep academic analysis" if mode == "research" else "taonga-aligned cultural summary"
        rsp = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": f"Summarize with {style}."},
                {"role": "user", "content": text},
            ],
        )
        out = rsp.output_text.strip()
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
