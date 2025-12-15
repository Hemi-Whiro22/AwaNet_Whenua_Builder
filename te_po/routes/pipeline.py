import os
import json

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, status
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from typing import List
import uuid
import shutil
from pathlib import Path

from te_po.pipeline.queue import pipeline_queue
from te_po.pipeline.jobs import process_document, enqueue_for_pipeline
from te_po.pipeline.job_tracking import get_job_status, get_recent_jobs
from te_po.db import db_execute, db_fetchone
from te_po.utils.audit import log_event
from te_po.utils.supabase_client import get_client
from te_po.core.env_loader import get_queue_mode

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")
SUPA = get_client()


@router.post("/run")
async def pipeline_run(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    source: str = Form(default="api"),
    authorization: str | None = Header(default=None),
):
    """
    Run the pipeline on an uploaded file (preferred) or inline text.
    """
    if PIPELINE_TOKEN:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
        token = authorization.split(" ", 1)[1].strip()
        if token != PIPELINE_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token.")

    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a file or text payload.")

    if file:
        data = await file.read()
        filename = file.filename or "upload"
    else:
        data = (text or "").encode("utf-8")
        filename = "inline.txt"

    result = run_pipeline(data, filename, source=source)
    log_event(
        "pipeline_run",
        "Pipeline executed",
        source=source,
        data={"filename": filename, "result": result},
    )
    return result


@router.post("/enqueue")
async def enqueue_pipeline(
    file: UploadFile = File(...),
    x_realm: str | None = Header(default=None, alias="X-Realm"),
):
    """
    Enqueue a pipeline job (inline mode) or to Redis/RQ (RQ mode).
    
    Queue mode controlled by QUEUE_MODE env var:
    - inline (default): Run immediately in-process, no Redis required
    - rq: Use Redis queue, requires Redis configured
    
    Returns:
    - Inline mode: {job_id, status, result?, error?}
    - RQ mode: {job_id, rq_job_id, queue, realm, status}
    
    Optional header: X-Realm (for multi-tenant tracking)
    """
    mode = get_queue_mode()
    
    db_job_id = str(uuid.uuid4())
    tmp_dir = Path("/tmp/pipeline_jobs")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    local_path = tmp_dir / f"{db_job_id}_{file.filename or 'upload'}"
    with local_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = None
    if local_path.suffix.lower() == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(str(local_path)) as pdf:
                pages = len(pdf.pages)
        except Exception:
            pages = None

    # Determine queue based on file size
    queue_name = "default"
    if pages is not None:
        if pages <= 3:
            queue_name = "urgent"
        elif pages > 50:
            queue_name = "slow"

    # Record in PostgreSQL (durable tracking)
    payload = {
        "filename": file.filename or "upload",
        "pages": pages,
        "file_path": str(local_path),
    }
    
    try:
        db_execute(
            """
            INSERT INTO pipeline_jobs (id, realm, queue, status, payload)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (db_job_id, x_realm, queue_name, "queued", json.dumps(payload))
        )
    except Exception as e:
        # Log but don't fail; Postgres tracking is best-effort
        import warnings
        warnings.warn(f"Failed to insert job into PostgreSQL: {e}", RuntimeWarning)

    # Also record in Supabase for backward compatibility (best-effort)
    if SUPA:
        try:
            SUPA.table("pipeline_jobs").insert({
                "id": db_job_id,
                "status": "queued",
                "file_path": str(local_path),
                "pages": pages
            }).execute()
        except Exception:
            pass

    # Process based on queue mode
    if mode == "inline":
        # Run immediately in-process
        result = enqueue_for_pipeline(str(local_path), db_job_id, pages=pages)
        if result.get("error"):
            # Update DB with error status
            try:
                db_execute(
                    "UPDATE pipeline_jobs SET status = %s, error = %s WHERE id = %s",
                    ("failed", result["error"], db_job_id)
                )
            except Exception:
                pass
            return {
                "job_id": db_job_id,
                "status": "failed",
                "error": result["error"],
            }
        else:
            # Update DB with finished status
            try:
                db_execute(
                    "UPDATE pipeline_jobs SET status = %s, result = %s WHERE id = %s",
                    ("finished", json.dumps(result.get("result", {})), db_job_id)
                )
            except Exception:
                pass
            return {
                "job_id": db_job_id,
                "status": "finished",
                "result": result.get("result"),
            }
    else:
        # RQ mode: enqueue to queue
        if pipeline_queue is None:
            raise HTTPException(status_code=503, detail="Pipeline queue unavailable (Redis not configured)")
        
        rq_result = enqueue_for_pipeline(str(local_path), db_job_id, pages=pages)
        
        return {
            "job_id": db_job_id,
            "rq_job_id": rq_result.get("rq_job_id"),
            "queue": queue_name,
            "realm": x_realm,
            "status": "queued",
        }


@router.get("/status/{job_id}")
async def pipeline_status(job_id: str):
    """
    Return the pipeline job status from PostgreSQL (durable tracking).
    
    Includes: status, result, error, started_at, finished_at, queue, realm.
    Falls back to Supabase if PostgreSQL unavailable (backward compat).
    """
    # Try PostgreSQL first
    pg_row = get_job_status(job_id)
    if pg_row:
        return pg_row
    
    # Fall back to Supabase for backward compatibility
    if SUPA is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        resp = SUPA.table("pipeline_jobs").select("*").eq("id", job_id).limit(1).execute()
        rows = getattr(resp, "data", None) or []
        if not rows:
            raise HTTPException(status_code=404, detail="Job not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/jobs/recent")
async def get_recent_jobs_endpoint(
    limit: int = 50,
    realm: str | None = None,
    queue: str | None = None,
    status: str | None = None,
):
    """
    Get recent pipeline jobs from PostgreSQL for dashboarding.
    
    Query parameters:
    - limit: Max results (default 50, max 500)
    - realm: Filter by realm (optional)
    - queue: Filter by queue (urgent/default/slow) (optional)
    - status: Filter by status (queued/running/finished/failed) (optional)
    """
    jobs = get_recent_jobs(limit=limit, realm=realm, queue=queue, status=status)
    return {
        "jobs": jobs,
        "count": len(jobs),
        "filters": {"realm": realm, "queue": queue, "status": status},
    }



@router.post("/batch")
async def enqueue_batch(files: List[UploadFile] = File(...)):
    """
    Enqueue multiple files; returns batch_id and job_ids.
    """
    batch_id = str(uuid.uuid4())
    job_ids: List[str] = []
    for f in files:
        res = await enqueue_pipeline(f)
        job_ids.append(res["job_id"])
        if SUPA:
            try:
                SUPA.table("pipeline_jobs").update({"batch_id": batch_id}).eq("id", res["job_id"]).execute()
            except Exception:
                pass
    return {"batch_id": batch_id, "job_ids": job_ids}


@router.get("/batch-status/{batch_id}")
async def batch_status(batch_id: str):
    if SUPA is None:
        raise HTTPException(status_code=503, detail="Supabase client not configured")
    try:
        resp = SUPA.table("pipeline_jobs").select("*").eq("batch_id", batch_id).execute()
        rows = getattr(resp, "data", None) or []
        complete = sum(1 for r in rows if r.get("status") == "done")
        return {"complete": complete, "total": len(rows), "jobs": rows}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str):
    if SUPA is None:
        raise HTTPException(status_code=503, detail="Supabase client not configured")
    try:
        SUPA.table("pipeline_jobs").update({"status": "cancelled"}).eq("id", job_id).execute()
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health/queue")
async def queue_health():
    """
    Health check for queue system.
    
    In inline mode: Returns 'disabled' (no Redis needed).
    In RQ mode: Checks Redis connectivity and queue lengths.
    """
    from te_po.pipeline.queue import redis_conn, urgent_queue, default_queue, slow_queue, dead_queue
    
    mode = get_queue_mode()
    
    health = {
        "mode": mode,
        "redis": "disabled" if mode == "inline" else "down",
        "queues": {} if mode == "inline" else None,
        "timestamp": None,
    }
    
    try:
        import time
        from datetime import datetime
        health["timestamp"] = datetime.utcnow().isoformat()
        
        if mode == "inline":
            health["status"] = "healthy"
            return health
        
        # RQ mode: test Redis connectivity
        if redis_conn:
            try:
                redis_conn.ping()
                health["redis"] = "up"
            except Exception as e:
                health["redis"] = f"error: {str(e)[:50]}"
                health["status"] = "degraded"
                return health
        
        # Get queue lengths
        if urgent_queue:
            health["queues"]["urgent"] = len(urgent_queue)
        if default_queue:
            health["queues"]["default"] = len(default_queue)
        if slow_queue:
            health["queues"]["slow"] = len(slow_queue)
        if dead_queue:
            health["queues"]["dead"] = len(dead_queue)
        
        health["status"] = "healthy" if health["redis"] == "up" else "degraded"
        return health
    
    except Exception as e:
        health["status"] = "error"
        health["error"] = str(e)[:100]
        return health
