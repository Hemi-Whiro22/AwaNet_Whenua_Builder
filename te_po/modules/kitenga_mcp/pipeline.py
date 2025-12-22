from datetime import datetime
from datetime import datetime
from typing import List

from fastapi import APIRouter

router = APIRouter()

_jobs_storage: List[dict] = []


def _get_recent_jobs(realm: str = "te_ao", limit: int = 5) -> List[dict]:
    filtered = [job for job in reversed(_jobs_storage) if job["realm"] == realm]
    return filtered[:limit]


def _enqueue_job(realm: str, payload: dict) -> dict:
    job = {
        "id": f"job_{len(_jobs_storage) + 1}",
        "realm": realm,
        "payload": payload,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
    }
    _jobs_storage.append(job)
    return job


@router.get("/jobs")
def get_recent_jobs(realm: str = "te_ao", limit: int = 5):
    return {"jobs": _get_recent_jobs(realm=realm, limit=limit)}


@router.post("/enqueue")
def enqueue_job(realm: str = "te_ao", payload: dict = None):
    payload = payload or {}
    job = _enqueue_job(realm=realm, payload=payload)
    return {"job": job}
