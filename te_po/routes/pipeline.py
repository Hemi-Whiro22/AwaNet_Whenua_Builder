import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, status
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from typing import List
import uuid
import shutil
from pathlib import Path

from te_po.pipeline.queue import pipeline_queue
from te_po.pipeline.jobs import process_document, enqueue_for_pipeline
from te_po.utils.audit import log_event
from te_po.utils.supabase_client import get_client

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
async def enqueue_pipeline(file: UploadFile = File(...)):
    """
    Enqueue a pipeline job to Redis/RQ. Returns job_id immediately.
    """
    if pipeline_queue is None:
        raise HTTPException(status_code=503, detail="Pipeline queue unavailable (Redis not configured)")

    job_id = str(uuid.uuid4())
    tmp_dir = Path("/tmp/pipeline_jobs")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    local_path = tmp_dir / f"{job_id}_{file.filename or 'upload'}"
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

    # Record in Supabase (best-effort)
    if SUPA:
        try:
            SUPA.table("pipeline_jobs").insert({"id": job_id, "status": "queued", "file_path": str(local_path), "pages": pages}).execute()
        except Exception:
            pass

    enqueue_for_pipeline(str(local_path), job_id, pages=pages)
    return {"job_id": job_id}


@router.get("/status/{job_id}")
async def pipeline_status(job_id: str):
    """
    Return the pipeline job status from Supabase (pipeline_jobs table).
    """
    if SUPA is None:
        raise HTTPException(status_code=503, detail="Supabase client not configured")
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
