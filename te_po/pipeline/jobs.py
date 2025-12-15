from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict

from rq import Retry

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.pipeline.queue import (
    urgent_queue,
    default_queue,
    slow_queue,
    dead_queue,
    redis_conn,
)
from te_po.pipeline.metrics import track_job
from te_po.pipeline.job_tracking import track_pipeline_job
from te_po.db import db_execute
from te_po.utils.supabase_client import get_client
from te_po.core.env_loader import get_queue_mode

SUPA = get_client()


def _update_job(job_id: str, data: Dict[str, Any]):
    if SUPA is None:
        return
    try:
        SUPA.table("pipeline_jobs").update(data).eq("id", job_id).execute()
    except Exception:
        return


@track_job
@track_pipeline_job
def process_document(file_path: str, job_id: str, source: str = "queue") -> Dict[str, Any]:
    """
    Heavy-lift pipeline runner for queued jobs.
    - Reads the file from disk
    - Runs pipeline (clean + chunk + embed + Supabase log)
    - Updates pipeline_jobs with progress/result
    """
    start = time.time()
    _update_job(job_id, {"status": "running", "progress": {"stage": "start", "percent": 5}})

    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"{file_path} not found")
        data = path.read_bytes()

        # Mark ingestion
        _update_job(job_id, {"progress": {"stage": "pipeline", "percent": 25}})

        # Check cancellation before heavy work
        try:
            if SUPA:
                status_row = (
                    SUPA.table("pipeline_jobs").select("status").eq("id", job_id).limit(1).execute()
                )
                row_data = getattr(status_row, "data", None) or []
                if row_data and row_data[0].get("status") == "cancelled":
                    _update_job(job_id, {"status": "cancelled", "progress": {"stage": "cancelled", "percent": 100}})
                    return {"status": "cancelled"}
        except Exception:
            pass

        result = run_pipeline(data, filename=path.name, source=source, generate_summary=True)

        _update_job(
            job_id,
            {
                "status": "done",
                "progress": {"stage": "complete", "percent": 100},
                "result": result,
                "duration_sec": round(time.time() - start, 2),
            },
        )
        return result
    except Exception as exc:
        _update_job(
            job_id,
            {
                "status": "error",
                "progress": {"stage": "error", "percent": 100},
                "result": {"error": str(exc)},
            },
        )
        # Dead-letter enqueue
        if dead_queue:
            try:
                dead_queue.enqueue(process_document, file_path, job_id, retry=Retry(max=3, interval=[10, 30, 60]))
            except Exception:
                pass
        return {"status": "error", "reason": str(exc)}


def enqueue_for_pipeline(file_path: str, job_id: str, pages: int | None = None) -> Dict[str, Any]:
    """
    Enqueue job for pipeline processing.
    
    Queue routing (RQ mode):
    - urgent: ≤3 pages, 10 min timeout, 2h result TTL
    - default: 3-50 pages, 30 min timeout, 24h result TTL
    - slow: >50 pages, 60 min timeout, 48h result TTL
    
    Inline mode: Runs immediately in-process without Redis.
    
    Returns:
    - RQ mode: {rq_job_id: str}
    - Inline mode: {result: dict, error: str or None}
    """
    mode = get_queue_mode()
    
    if mode == "inline":
        # Run pipeline immediately in-process
        try:
            result = process_document(file_path, job_id, source="inline")
            return {"result": result, "error": None}
        except Exception as e:
            return {"result": None, "error": str(e)}
    
    # RQ mode: enqueue to appropriate queue
    q = default_queue
    timeout = "30m"  # default
    result_ttl = 86400  # 24 hours in seconds
    
    if pages is not None:
        if pages <= 3 and urgent_queue:
            q = urgent_queue
            timeout = "10m"
            result_ttl = 7200  # 2 hours
        elif pages > 50 and slow_queue:
            q = slow_queue
            timeout = "60m"
            result_ttl = 172800  # 48 hours
        elif default_queue:
            q = default_queue
    
    if q:
        rq_job = q.enqueue(
            process_document,
            file_path,
            job_id,
            job_timeout=timeout,
            result_ttl=result_ttl,
            retry=Retry(max=3, interval=[10, 30, 60])
        )
        return {"rq_job_id": rq_job.id}
    
    return {"rq_job_id": None}


__all__ = ["process_document", "enqueue_for_pipeline", "redis_conn"]
