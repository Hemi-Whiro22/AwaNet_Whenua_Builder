from fastapi import APIRouter, UploadFile
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

router = APIRouter()


@router.post("/ocr/scan")
async def scan(file: UploadFile):
    data = await file.read()
    return run_pipeline(data, file.filename or "scan_upload", source="ocr")
