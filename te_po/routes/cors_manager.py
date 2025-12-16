"""
CORS Manager Routes - Dynamic CORS origin management.
Allows adding/removing CORS origins at runtime via API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Set
import os

router = APIRouter(prefix="/cors", tags=["cors"])

# Runtime CORS origins - starts with env/defaults, can be modified live
_runtime_origins: Set[str] = set()
_initialized = False


def _init_origins():
    """Initialize from environment or defaults."""
    global _initialized, _runtime_origins
    if _initialized:
        return
    
    env_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if env_origins:
        _runtime_origins = set(origin.strip() for origin in env_origins.split(",") if origin.strip())
    else:
        _runtime_origins = {
            "http://localhost:5000",
            "http://localhost:5001", 
            "http://localhost:5173",
            "http://localhost:8100",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:5001",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8100",
        }
    _initialized = True


def get_allowed_origins() -> List[str]:
    """Get current allowed origins - used by CORS middleware."""
    _init_origins()
    return list(_runtime_origins)


def is_origin_allowed(origin: str) -> bool:
    """Check if an origin is allowed."""
    _init_origins()
    return origin in _runtime_origins or "*" in _runtime_origins


class OriginRequest(BaseModel):
    origin: str


class OriginsResponse(BaseModel):
    origins: List[str]
    count: int


@router.get("/origins", response_model=OriginsResponse)
async def list_origins():
    """List all currently allowed CORS origins."""
    _init_origins()
    origins = sorted(_runtime_origins)
    return OriginsResponse(origins=origins, count=len(origins))


@router.post("/origins/add")
async def add_origin(req: OriginRequest):
    """Add a new CORS origin at runtime."""
    _init_origins()
    
    origin = req.origin.strip()
    if not origin:
        raise HTTPException(status_code=400, detail="Origin cannot be empty")
    
    # Basic validation
    if not origin.startswith(("http://", "https://", "*")):
        raise HTTPException(status_code=400, detail="Origin must start with http://, https://, or be '*'")
    
    if origin in _runtime_origins:
        return {"status": "exists", "message": f"Origin '{origin}' already allowed", "origins": sorted(_runtime_origins)}
    
    _runtime_origins.add(origin)
    return {"status": "added", "message": f"Origin '{origin}' added", "origins": sorted(_runtime_origins)}


@router.post("/origins/remove")
async def remove_origin(req: OriginRequest):
    """Remove a CORS origin at runtime."""
    _init_origins()
    
    origin = req.origin.strip()
    if origin not in _runtime_origins:
        raise HTTPException(status_code=404, detail=f"Origin '{origin}' not in allowed list")
    
    _runtime_origins.discard(origin)
    return {"status": "removed", "message": f"Origin '{origin}' removed", "origins": sorted(_runtime_origins)}


@router.post("/origins/reset")
async def reset_origins():
    """Reset CORS origins to defaults."""
    global _runtime_origins, _initialized
    _initialized = False
    _runtime_origins = set()
    _init_origins()
    return {"status": "reset", "message": "CORS origins reset to defaults", "origins": sorted(_runtime_origins)}
