from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from te_po.services.local_storage import DIRS

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/recent")
async def recent_logs(
    limit: int = Query(50, ge=1, le=500),
    contains: str | None = Query(None, description="Filter by substring in event/detail"),
):
    """Return the most recent audit events (reverse chronological)."""
    audit_path = DIRS["logs"] / "project_audit.jsonl"
    if not audit_path.exists():
        return {"events": []}
    try:
        lines = audit_path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {exc}")

    events: list[dict[str, Any]] = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            import json

            obj = json.loads(line)
        except Exception:
            continue
        if contains:
            haystack = f"{obj.get('event','')} {obj.get('detail','')}"
            if contains.lower() not in haystack.lower():
                continue
        events.append(obj)
        if len(events) >= limit:
            break
    return {"events": events}
