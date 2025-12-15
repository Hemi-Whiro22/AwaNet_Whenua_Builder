import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/assistants", tags=["Assistants"])


@router.get("/profiles")
async def assistant_profiles():
    """Return assistant profile definitions for QA/Ops wiring."""
    path = Path(__file__).resolve().parents[1] / "openai_assistants.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Assistant profiles not found.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read assistant profiles: {exc}")
