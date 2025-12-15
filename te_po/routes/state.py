import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/ledger")
async def ledger(limit: int = 200):
    """Return recent carving ledger entries from Mauri state."""
    ledger_path = Path(__file__).resolve().parents[2] / "mauri" / "state" / "te_po_carving_log.jsonl"
    if not ledger_path.exists():
        return {"events": []}
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read ledger: {exc}")

    events = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
        if len(events) >= limit:
            break
    return {"events": events}


@router.get("/state")
async def state():
    """Return Te Pō state summary from Mauri."""
    state_path = Path(__file__).resolve().parents[2] / "mauri" / "state" / "te_po_state.json"
    if not state_path.exists():
        raise HTTPException(status_code=404, detail="State file not found.")
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read state: {exc}")
