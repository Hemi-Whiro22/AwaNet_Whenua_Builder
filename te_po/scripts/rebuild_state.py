"""
Regenerate Te Pō state/ledger summaries for Mauri awareness.

Outputs:
- mauri/state/te_po_state.json with tools, assistants, env refs, and routes overview.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.core.config import settings  # noqa: E402
MAURI_STATE = ROOT / "mauri" / "state" / "te_po_state.json"
TOOLS_PATH = ROOT / "kitenga_mcp" / "openai_tools.json"
ASSISTANTS_PATH = ROOT / "te_po" / "openai_assistants.json"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def build_state():
    load_env(str(ROOT / "te_po" / "core" / ".env"))

    existing = load_json(MAURI_STATE, {})
    tools_spec = load_json(TOOLS_PATH, {})
    assistants_spec = load_json(ASSISTANTS_PATH, {})

    routes = [
        "/",
        "/heartbeat",
        "/status",
        "/status/openai",
        "/kitenga/gpt-whisper",
        "/kitenga/vision-ocr",
        "/pipeline/run",
        "/assistant/run",
        "/vector/embed",
        "/vector/search",
        "/vector/retrieval-test",
        "/vector/batch-status",
        "/logs/recent",
        "/logs/ledger",
        "/logs/state",
        "/assistants/profiles",
    ]

    state = {
        "realm": existing.get("realm", "te_po"),
        "guardian": existing.get("guardian", "kitenga_whiro"),
        "manifest": existing.get("manifest", "mauri/realms/te_po_manifest.json"),
        "env_hash": existing.get("env_hash"),
        "health": existing.get("health", "unknown"),
        "vector_store_id": settings.openai_vector_store_id,
        "vector_store_env": "OPENAI_VECTOR_STORE_ID",
        "pipeline_token_env": "PIPELINE_TOKEN",
        "base_url_env": "TE_PO_BASE_URL",
        "supabase_url_env": "SUPABASE_URL",
        "supabase_bucket_storage": settings.supabase_bucket_storage,
        "supabase_table_files": settings.supabase_table_files,
        "tools_spec": str(TOOLS_PATH.relative_to(ROOT)),
        "assistants_spec": str(ASSISTANTS_PATH.relative_to(ROOT)),
        "tools": tools_spec.get("tools", []),
        "assistants": assistants_spec,
        "routes": routes,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    MAURI_STATE.parent.mkdir(parents=True, exist_ok=True)
    MAURI_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


if __name__ == "__main__":
    final_state = build_state()
    print(json.dumps(final_state, indent=2))
