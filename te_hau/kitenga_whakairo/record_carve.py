"""
Record a carve summary (non-taonga by default).

Writes to:
- mauri/state/carver_log.jsonl (local, append-only)
- Supabase table carver_context_memory (best-effort, if configured)

Usage:
    python te_hau/whakairo/record_carve.py --title "Short title" --summary "What changed" --files "file1,file2" --tags "carve,api" --mode research
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402
from te_po.utils.supabase_client import get_client  # noqa: E402
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline  # noqa: E402
from te_po.services.supabase_logging import log_pipeline_run  # noqa: E402


def write_local_log(entry: dict):
    log_path = ROOT / "mauri" / "state" / "carver_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_supabase(entry: dict):
    client = get_client()
    if client is None:
        return {"status": "skipped", "reason": "supabase client not configured"}
    try:
        resp = client.table("carver_context_memory").insert(entry).execute()
        return {"status": "ok", "data": getattr(resp, "data", None)}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Short title for the carve")
    parser.add_argument("--summary", required=True, help="What changed")
    parser.add_argument("--files", default="", help="Comma-separated files touched")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--mode", default="research", help="research|taonga (taonga kept high-level only)")
    parser.add_argument("--text", default=None, help="Optional text to ingest into pipeline/vector (non-taonga only)")
    parser.add_argument("--save-vector", action="store_true", help="Save vector embedding for provided text")
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))

    entry = {
        "title": args.title,
        "summary": args.summary,
        "files_touched": [f.strip() for f in args.files.split(",") if f.strip()],
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "mode": args.mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": None,
    }

    # Optional ingest of text into pipeline/vector
    if args.text:
        try:
            # Only ingest non-taonga content to avoid leakage
            source = "whakairo_carve"
            run_res = run_pipeline(
                args.text.encode("utf-8"),
                filename=f"carve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                source=source,
                mode=args.mode,
                generate_summary=False,
            )
            entry["pipeline"] = {
                "status": run_res.get("status"),
                "raw_file": run_res.get("raw_file"),
                "clean_file": run_res.get("clean_file"),
                "vector_batch_id": run_res.get("vector_batch_id"),
            }
            # Log pipeline run in Supabase best-effort
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
                    metadata={"mode": args.mode},
                )
            except Exception:
                pass
        except Exception as exc:
            entry["pipeline"] = {"status": "error", "reason": str(exc)}

    write_local_log(entry)
    supa_res = write_supabase(entry)

    print("Recorded carve locally at mauri/state/carver_log.jsonl")
    print(f"Supabase: {supa_res}")
    if supa_res.get("status") == "ok":
        print("Reminder: run sync_carver_context.py to refresh local anchor cache from Supabase.")


if __name__ == "__main__":
    main()
