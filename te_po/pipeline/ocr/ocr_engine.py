import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

from te_po.core.config import settings
from te_po.pipeline.ocr.stealth_engine import StealthOCR


def _tesseract_available(path: Optional[str]) -> bool:
    try:
        subprocess.run(
            [path or "tesseract", "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return True
    except Exception:
        return False


def run_ocr(image_bytes: bytes, mode: str = "research", apply_encoding: bool = True) -> Dict[str, Any]:
    """
    Stealth OCR wrapper using the real scanner (tesseract + vision + cultural protection).
    Returns dict with text_extracted/raw_text and metadata, plus timestamp and mode.
    - mode: "research" or "taonga"
    - apply_encoding: when False, bypass cultural encoding
    """
    try:
        scanner = StealthOCR()
        if not apply_encoding:
            scanner.cultural_encoding_active = False

        result = scanner.real_scan(image_bytes, prefer_offline=True)
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        result["mode"] = mode
        return result
    except Exception as exc:
        return {"text": "", "error": str(exc)}
