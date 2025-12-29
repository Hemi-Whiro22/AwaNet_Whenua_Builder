import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from te_po.core.env_loader import load_env
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.services.supabase_logging import log_pipeline_run
from te_po.utils.supabase_client import get_client

# /workspaces/The_Awa_Network
REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_LOADED = False


def _ensure_env():
    """Load Whakairo-specific env plus te_po core env once."""
    global ENV_LOADED
    if ENV_LOADED:
        return

    candidates = []
    override = os.getenv("DOTENV_PATH")
    if override:
        candidates.append(REPO_ROOT / override)
    candidates.extend(
        [
            REPO_ROOT / "te_hau" / "kitenga_whakairo" / ".env.whakairo",
            REPO_ROOT / ".env.whakairo",
            REPO_ROOT / ".env",
        ]
    )
    loaded = None
    for path in candidates:
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)
            loaded = path
            break

    te_po_env = REPO_ROOT / "te_po" / "core" / ".env"
    if te_po_env.exists():
        load_env(str(te_po_env))

    ENV_LOADED = True
    return loaded


def record_carve_entry(
    ctx: Any,
    title: str,
    summary: str,
    files: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    mode: str = "research",
    text: Optional[str] = None,
    save_vector: bool = False,
):
    """
    Append a carve entry locally and best-effort Supabase insert.
    Optionally ingest provided text into the pipeline/vector flow.
    """
    _ensure_env()

    entry = {
        "title": title,
        "summary": summary,
        "files_touched": files or [],
        "tags": tags or [],
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": None,
    }

    if text:
        try:
            source = "whakairo_carve"
            run_res = run_pipeline(
                text.encode("utf-8"),
                filename=f"carve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                source=source,
                mode=mode,
                generate_summary=False,
            )
            entry["pipeline"] = {
                "status": run_res.get("status"),
                "raw_file": run_res.get("raw_file"),
                "clean_file": run_res.get("clean_file"),
                "vector_batch_id": run_res.get("vector_batch_id"),
            }
            try:
                log_pipeline_run(
                    source=source,
                    status=run_res.get("status") or "ok",
                    glyph=run_res.get("glyph"),
                    raw_file=run_res.get("raw_file"),
                    clean_file=run_res.get("clean_file"),
                    chunk_ids=[c.get("id") for c in run_res.get("chunks", []) if isinstance(c, dict)],
                    vector_batch_id=run_res.get("vector_batch_id"),
                    storage=run_res.get("supabase", {}).get("storage") if isinstance(run_res.get("supabase"), dict) else None,
                    supabase_status=run_res.get("supabase") if isinstance(run_res.get("supabase"), dict) else None,
                    metadata={"mode": mode},
                )
            except Exception:
                pass
        except Exception as exc:
            entry["pipeline"] = {"status": "error", "reason": str(exc)}

    # Local log
    log_path = REPO_ROOT / "mauri" / "state" / "carver_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Supabase
    client = get_client()
    supa_res: Dict[str, Any]
    if client is None:
        supa_res = {"status": "skipped", "reason": "supabase client not configured"}
    else:
        try:
            resp = client.table("carver_context_memory").insert(entry).execute()
            supa_res = {"status": "ok", "data": getattr(resp, "data", None)}
        except Exception as exc:
            supa_res = {"status": "error", "reason": str(exc)}

    return {"entry": entry, "supabase": supa_res, "log_path": str(log_path)}


def sync_carver_context_tool(ctx: Any, limit_memory: int = 100, limit_logs: int = 200):
    """Sync carver context and kitenga logs into local state cache."""
    _ensure_env()
    client = get_client()
    if client is None:
        return {"error": "Supabase client not configured."}

    def fetch_table(table: str, limit: int):
        try:
            resp = client.table(table).select("*").order("created_at", desc=True).limit(limit).execute()
            return getattr(resp, "data", None) or []
        except Exception as exc:
            return {"error": str(exc)}

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "carver_context_memory": fetch_table("carver_context_memory", limit_memory),
        "kitenga_logs": fetch_table("kitenga_logs", limit_logs),
    }

    out_path = REPO_ROOT / "mauri" / "state" / "carver_context_cache.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "path": str(out_path),
        "counts": {
            "carver_context_memory": len(payload.get("carver_context_memory", [])),
            "kitenga_logs": len(payload.get("kitenga_logs", [])),
        },
    }
