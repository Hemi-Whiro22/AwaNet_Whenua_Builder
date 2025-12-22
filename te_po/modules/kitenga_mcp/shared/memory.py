"""
Memory Management for MCP Services
===================================
Handles context, memory storage, and pipeline job management.

Features:
- Persistent memory store per realm
- Semantic search simulation
- Pipeline job queue
- Context manager for maintaining state
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

# In-memory storage (would be persistent in production)
_memory_store: List[Dict[str, Any]] = []
_jobs_storage: List[Dict[str, Any]] = []


class MemoryManager:
    """Manages memory storage and retrieval per realm."""

    def __init__(self):
        self.store = _memory_store
        self.jobs = _jobs_storage

    def store_fragment(
        self,
        realm: str,
        content: str,
        tapu_level: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store a memory fragment."""
        fragment = {
            "id": f"mem_{len(self.store) + 1}",
            "realm": realm,
            "content": content,
            "tapu_level": tapu_level,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self.store.append(fragment)
        logger.info(f"Stored memory fragment: {fragment['id']} in realm {realm}")
        return fragment

    def search_memory(
        self, realm: str, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Semantically search memory (simulated)."""
        # In production, this would use vector similarity
        realm_memories = [m for m in self.store if m["realm"] == realm]

        matches = [
            {
                "id": m["id"],
                "content": m["content"],
                "tapu_level": m["tapu_level"],
                "similarity": round(0.95 - idx * 0.1, 3),
                "created_at": m["created_at"],
            }
            for idx, m in enumerate(realm_memories[:top_k])
        ]
        return matches

    def get_realm_memories(self, realm: str) -> List[Dict[str, Any]]:
        """Get all memories for a realm."""
        return [m for m in self.store if m["realm"] == realm]

    def clear_realm(self, realm: str) -> int:
        """Clear all memories for a realm."""
        before = len(self.store)
        self.store[:] = [m for m in self.store if m["realm"] != realm]
        after = len(self.store)
        logger.info(f"Cleared {before - after} memories from realm {realm}")
        return before - after


class PipelineManager:
    """Manages task pipelines and job execution."""

    def __init__(self):
        self.jobs = _jobs_storage

    def enqueue_job(
        self, realm: str, payload: Dict[str, Any], priority: int = 0
    ) -> Dict[str, Any]:
        """Enqueue a job for execution."""
        job = {
            "id": f"job_{len(self.jobs) + 1}",
            "realm": realm,
            "payload": payload,
            "status": "queued",
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
        }
        self.jobs.append(job)
        logger.info(f"Enqueued job: {job['id']} in realm {realm}")
        return job

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID."""
        for job in self.jobs:
            if job["id"] == job_id:
                return job
        return None

    def update_job_status(
        self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update job status."""
        job = self.get_job(job_id)
        if not job:
            return None

        job["status"] = status
        if status == "started" and not job["started_at"]:
            job["started_at"] = datetime.utcnow().isoformat()
        elif status == "completed":
            job["completed_at"] = datetime.utcnow().isoformat()
            if result:
                job["result"] = result

        logger.info(f"Updated job {job_id} status to {status}")
        return job

    def get_recent_jobs(self, realm: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent jobs for a realm."""
        filtered = [j for j in reversed(self.jobs) if j["realm"] == realm]
        return filtered[:limit]

    def get_pending_jobs(self, realm: str) -> List[Dict[str, Any]]:
        """Get pending jobs for a realm."""
        return [
            j
            for j in self.jobs
            if j["realm"] == realm and j["status"] in ("queued", "started")
        ]


# Global instances
memory = MemoryManager()
pipeline = PipelineManager()
