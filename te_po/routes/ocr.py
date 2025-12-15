from fastapi import APIRouter, UploadFile
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

# Optional imports - stealth_ocr files are gitignored (not used in production)
try:
    from te_po.stealth_ocr import StealthOCR
except ImportError:
    StealthOCR = None

try:
    from te_po.stealth_ocr_testit import StealthOCR as StealthOCRTest
except ImportError:
    StealthOCRTest = None

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
    if StealthOCR is None:
        return {"error": "StealthOCR module not available in this deployment"}
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
    if StealthOCRTest is None:
        return {"error": "StealthOCRTest module not available in this deployment"}
    data = await file.read()
    ocr = StealthOCRTest()
    return ocr.psycheract_scan(data, prefer_offline=True)
