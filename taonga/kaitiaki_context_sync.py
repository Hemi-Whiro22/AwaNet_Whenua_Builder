from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from te_po.utils.openai_client import last_openai_run_id
from te_po.utils.supabase_client import get_client

ANALYSIS_DIR = Path(__file__).resolve().parent
SYNC_LOG = ANALYSIS_DIR / f"kaitiaki_sync_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"


def load_recent_metadata() -> Dict[str, Any]:
    data: Dict[str, Any] = {"todo": [], "context": {}}
    for path in sorted(ANALYSIS_DIR.glob("review_log_*.md"), reverse=True)[:3]:
        with path.open(encoding="utf-8", errors="ignore") as handle:
            lines = [line.strip() for line in handle if line.strip()]
        data["context"][path.name] = lines[:6]
    return data


def scan_tool_manifests() -> List[str]:
    misses: List[str] = []
    for path in (Path("kitenga_mcp/tools") / "manifests").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("metadata", {}).get("author"):
            misses.append(f"{path.name} missing author tag")
    return misses


def check_openai_vectors() -> List[str]:
    client = get_client()
    entries: List[str] = []
    if client is None:
        return ["Supabase client missing for vector checks"]
    try:
        resp = client.table("kitenga_vector_batches").select("batch_id", "metadata").limit(5).execute()
        for row in getattr(resp, "data", []) or []:
            meta = row.get("metadata", {})
            if not meta.get("openai_run_ids"):
                entries.append(f"Batch {row.get('batch_id')} missing OPENAI run id")
    except Exception as exc:
        entries.append(f"Vector batch scan failed: {exc}")
    return entries


def build_todo() -> Dict[str, Any]:
    todo: Dict[str, Any] = {}
    todo["kaitiaki"] = [
        "Rerun context sync when tool manifests change",
        "Ensure chat memory pushes include pipeline_metadata",
        "Refresh OpenAI vector run IDs nightly",
    ]
    todo["issues"] = scan_tool_manifests() + check_openai_vectors()
    if not todo["issues"]:
        todo["issues"].append("All manifests & vector batches tagged")
    return todo


def write_sync_log(payload: Dict[str, Any]) -> None:
    SYNC_LOG.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    payload = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "author": "awa developer (Kitenga Whiro [Adrian Hemi])",
        "openai_last_run_id": last_openai_run_id(),
        "todo": build_todo(),
        "context": load_recent_metadata(),
    }
    write_sync_log(payload)


if __name__ == "__main__":
    main()
