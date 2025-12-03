import base64
import io
import json
import uuid

import pytesseract
from PIL import Image

from te_po.services.local_storage import save, timestamp


def ocr_image(file_bytes: bytes, filename: str | None = None):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img, lang="eng")
        entry_id = f"ocr_{uuid.uuid4().hex}"
        save(
            "logs",
            f"{entry_id}.json",
            json.dumps({"id": entry_id, "text": text, "filename": filename}, indent=2),
        )
        save("clean", f"{entry_id}.txt", text.strip())
        raw_payload = base64.b64encode(file_bytes).decode("utf-8")
        raw_name = f"{timestamp()}_{filename or 'upload'}.b64"
        save("raw", raw_name, raw_payload)
        return {"id": entry_id, "text": text, "saved": True}
    except Exception as exc:
        return {"id": None, "text": f"OCR failed: {exc}", "saved": False}
