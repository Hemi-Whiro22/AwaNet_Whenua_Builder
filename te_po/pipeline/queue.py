from __future__ import annotations

import os
from typing import Optional

from redis import Redis
from rq import Queue


def _build_redis() -> Optional[Redis]:
    """
    Create a Redis connection. Falls back to localhost:6379.
    """
    url = os.getenv("REDIS_URL")
    if url:
        try:
            return Redis.from_url(url)
        except Exception:
            return None
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    try:
        return Redis(host=host, port=port)
    except Exception:
        return None


redis_conn: Optional[Redis] = _build_redis()

# Multi-lane queues
urgent_queue: Optional[Queue] = Queue("urgent", connection=redis_conn) if redis_conn else None
default_queue: Optional[Queue] = Queue("default", connection=redis_conn) if redis_conn else None
slow_queue: Optional[Queue] = Queue("slow", connection=redis_conn) if redis_conn else None
dead_queue: Optional[Queue] = Queue("dead", connection=redis_conn) if redis_conn else None

# Legacy alias for default queue to avoid breakage
pipeline_queue: Optional[Queue] = default_queue

__all__ = ["redis_conn", "urgent_queue", "default_queue", "slow_queue", "dead_queue", "pipeline_queue"]
