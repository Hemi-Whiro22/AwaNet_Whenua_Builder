import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, status
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")


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

    return run_pipeline(data, filename, source=source)
