from datetime import datetime
import platform

from fastapi import APIRouter

router = APIRouter(tags=["Status"])


@router.get("/status")
async def status():
    """Lightweight health endpoint for Te Pō."""
    return {
        "realm": "te_po",
        "status": "online",
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": platform.node(),
    }
