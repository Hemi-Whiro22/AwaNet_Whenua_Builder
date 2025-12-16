import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from te_po.state.read_state import get_private_state, get_public_state, get_state_version

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


@router.get("/state/public", response_class=JSONResponse)
async def get_public_state_endpoint():
    """Fetch the public project state."""
    return get_public_state()


@router.get("/state/private", response_class=JSONResponse)
async def get_private_state_endpoint():
    """Fetch the private project state. Protected by BearerAuthMiddleware."""
    return get_private_state()


@router.get("/state/version", response_class=JSONResponse)
async def get_state_version_endpoint():
    """Fetch the current state version."""
    return get_state_version()
