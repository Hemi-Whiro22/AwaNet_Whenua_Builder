from fastapi import APIRouter, UploadFile
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.stealth_ocr import StealthOCR
from te_po.stealth_ocr_testit import StealthOCR as StealthOCRTest

router = APIRouter()


@router.post("/ocr/scan")
async def scan(file: UploadFile):
    data = await file.read()
    return run_pipeline(data, file.filename or "scan_upload", source="ocr")


@router.post("/ocr/stealth")
async def stealth_scan(file: UploadFile):
    """
    Direct StealthOCR test endpoint using real Tesseract + vision fallback (with cultural protection).
    Returns the protected text and metadata; does NOT run the full pipeline.
    """
    data = await file.read()
    ocr = StealthOCR()
    result = ocr.real_scan(data, prefer_offline=True)
    return result


@router.post("/ocr/stealth-testit")
async def stealth_scan_testit(file: UploadFile):
    """
    Alternate StealthOCR test endpoint using the testit class (real Tesseract + vision).
    Useful to compare behaviors without touching the main pipeline.
    """
    data = await file.read()
    ocr = StealthOCRTest()
    return ocr.psycheract_scan(data, prefer_offline=True)
