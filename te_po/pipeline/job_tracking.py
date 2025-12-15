"""Job tracking wrapper for pipeline jobs.

Wraps RQ job execution to automatically:
- Update status to 'running' + started_at on start
- Update status to 'finished' + result on success
- Update status to 'failed' + error on failure (re-raise for RQ handling)
"""

import time
import traceback
from typing import Any, Callable, Optional
from functools import wraps

from te_po.db import db_execute, db_fetchone, db_query


def track_pipeline_job(
    job_func: Callable,
) -> Callable:
    """Decorator to wrap a pipeline job function with DB status tracking.
    
    Usage:
        @track_pipeline_job
        def process_document(file_path: str, job_id: str) -> dict:
            # ... processing logic
            return {"status": "success", ...}
    
    The wrapper:
    1. Updates status='running' + started_at=now() at start
    2. On success: status='finished', finished_at=now(), result=json
    3. On failure: status='failed', finished_at=now(), error=message (re-raises)
    """
    @wraps(job_func)
    def wrapper(*args, **kwargs) -> Any:
        # Extract job_id from kwargs or assume first positional arg
        job_id = kwargs.get("job_id") or (args[1] if len(args) > 1 else None)
        
        if not job_id:
            # No job tracking; just run the function
            return job_func(*args, **kwargs)
        
        start_time = time.time()
        
        # Mark as running
        try:
            db_execute(
                """
                UPDATE pipeline_jobs 
                SET status = %s, started_at = now()
                WHERE id = %s
                """,
                ("running", job_id)
            )
        except Exception:
            pass  # Best-effort; continue regardless
        
        try:
            # Execute the actual job function
            result = job_func(*args, **kwargs)
            
            # Mark as finished
            try:
                duration_sec = time.time() - start_time
                db_execute(
                    """
                    UPDATE pipeline_jobs
                    SET status = %s, finished_at = now(), result = %s
                    WHERE id = %s
                    """,
                    ("finished", str(result), job_id)
                )
            except Exception:
                pass  # Best-effort update
            
            return result
        
        except Exception as exc:
            # Mark as failed + log error
            error_msg = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
            try:
                db_execute(
                    """
                    UPDATE pipeline_jobs
                    SET status = %s, finished_at = now(), error = %s
                    WHERE id = %s
                    """,
                    ("failed", error_msg[:2000], job_id)  # Limit error msg length
                )
            except Exception:
                pass  # Best-effort
            
            # Re-raise so RQ still handles retries/dead queue
            raise
    
    return wrapper


def get_job_status(job_id: str) -> Optional[dict]:
    """Retrieve job status from database.
    
    Returns dict with keys: status, result, error, started_at, finished_at, etc.
    Or None if not found.
    """
    return db_fetchone(
        "SELECT * FROM pipeline_jobs WHERE id = %s",
        (job_id,)
    )


def get_recent_jobs(
    limit: int = 50,
    realm: Optional[str] = None,
    queue: Optional[str] = None,
    status: Optional[str] = None,
) -> list:
    """Get recent jobs from database for dashboarding.
    
    Args:
        limit: Max results (default 50, max 500)
        realm: Filter by realm (optional)
        queue: Filter by queue name (optional)
        status: Filter by status (queued/running/finished/failed) (optional)
    
    Returns:
        List of job dicts, ordered by created_at DESC
    """
    limit = min(limit, 500)  # Safety cap
    
    query = "SELECT * FROM pipeline_jobs WHERE 1=1"
    params = []
    
    if realm:
        query += " AND realm = %s"
        params.append(realm)
    if queue:
        query += " AND queue = %s"
        params.append(queue)
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    return db_query(query, tuple(params)) or []
