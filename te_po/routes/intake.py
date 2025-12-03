from fastapi import APIRouter, UploadFile, File, Body

from te_po.models.intake_models import SummarizeRequest
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.services.summary_service import summarize_text

router = APIRouter(prefix="/intake", tags=["Intake"])


@router.post("/ocr")
async def intake_ocr(file: UploadFile = File(...)):
    data = await file.read()
    return run_pipeline(data, file.filename or "intake_upload", source="intake")


@router.post("/summarize")
async def intake_summarize(payload: SummarizeRequest = Body(...)):
    return summarize_text(payload.text, payload.mode)
