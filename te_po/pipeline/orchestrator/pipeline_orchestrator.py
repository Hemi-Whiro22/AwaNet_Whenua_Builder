import base64
import io
import json
import uuid
from typing import Any

from te_po.mauri import MAURI
from te_po.pipeline.cleaner.text_cleaner import clean_text
from te_po.pipeline.chunker.chunk_engine import chunk_text
from te_po.pipeline.embedder.embed_engine import embed_text
from te_po.pipeline.ocr.ocr_engine import run_ocr
from te_po.pipeline.supabase_writer.writer import save_chunk
from te_po.services.local_storage import save, timestamp
from te_po.services.vector_service import push_chunk_embedding

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_EXT = {".txt", ".md", ".json", ".yaml", ".yml"}
PDF_EXT = {".pdf"}
AUDIO_EXT = {".wav", ".mp3", ".m4a"}


def _extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber; OCR fallback via Tesseract for image-only pages."""
    text_parts: list[str] = []
    ocr_parts: list[str] = []

    try:
        import pdfplumber
    except Exception:
        pdfplumber = None

    # Primary extraction via pdfplumber
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text() or ""
                    if extracted.strip():
                        text_parts.append(extracted.strip())
                    else:
                        # Fallback OCR per page
                        try:
                            import pytesseract
                            from PIL import Image

                            img = page.to_image(resolution=300).original.convert("RGB")
                            buf = io.BytesIO()
                            img.save(buf, format="PNG")
                            ocr_text = pytesseract.image_to_string(Image.open(io.BytesIO(buf.getvalue())))
                            if ocr_text.strip():
                                ocr_parts.append(ocr_text.strip())
                        except Exception:
                            continue
        except Exception:
            pass

    combined = "\n\n".join(text_parts + ocr_parts).strip()
    return combined


def _persist_raw(image_bytes: bytes, filename: str | None) -> str:
    safe_name = filename or f"upload_{uuid.uuid4().hex}"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    raw_file = f"{timestamp()}_{safe_name}.b64"
    save("raw", raw_file, encoded)
    return raw_file


def run_pipeline(file_bytes: bytes, filename: str | None = None, source: str = "upload") -> dict[str, Any]:
    raw_file = _persist_raw(file_bytes, filename)
    name = (filename or "").lower()
    glyph = (
        MAURI.get("identity", {}).get("glyph_id")
        or MAURI.get("openai", {}).get("glyph_id")
        or "unknown"
    )

    # Detect file type and extract text accordingly
    ext = ""
    if "." in name:
        ext = name[name.rfind(".") :]

    if ext in IMAGE_EXT:
        raw_text = run_ocr(file_bytes)
    elif ext in TEXT_EXT:
        raw_text = file_bytes.decode("utf-8", errors="ignore")
    elif ext in PDF_EXT:
        raw_text = _extract_pdf_text(file_bytes)
        if not raw_text:
            return {
                "status": "unsupported",
                "reason": "PDF text could not be extracted (install pypdf or check file)",
                "file": filename,
            }
    elif ext in AUDIO_EXT:
        return {
            "status": "unsupported",
            "reason": "Audio transcription not implemented in this pipeline",
            "file": filename,
        }
    else:
        return {
            "status": "unsupported",
            "reason": f"Unsupported file type: {ext or 'unknown'}",
            "file": filename,
        }

    cleaned = clean_text(raw_text)
    clean_file = f"{timestamp()}_{uuid.uuid4().hex}.txt"
    save("clean", clean_file, cleaned)

    chunks = chunk_text(cleaned)
    meta = {
        "source": source,
        "glyph": glyph,
        "raw_file": raw_file,
    }

    stored_chunks = []
    for chunk in chunks:
        embedding = embed_text(chunk)
        chunk_record = save_chunk(chunk, embedding, meta)
        remote = push_chunk_embedding(
            chunk_id=chunk_record["id"],
            text=chunk,
            embedding=embedding,
            metadata={"source": source, "glyph": glyph},
        )
        stored_chunks.append(
            {
                "id": chunk_record["id"],
                "path": chunk_record["path"],
                "length": len(chunk),
                "remote": remote,
            }
        )

    save(
        "logs",
        f"pipeline_{timestamp()}_{uuid.uuid4().hex}.json",
        json.dumps(
            {
                "event": "pipeline_run",
                "source": source,
                "glyph": meta["glyph"],
                "raw_file": raw_file,
                "clean_file": clean_file,
                "chunks": [c["id"] for c in stored_chunks],
            },
            indent=2,
        ),
    )

    return {
        "status": "ok",
        "glyph": meta["glyph"],
        "source": source,
        "raw_file": raw_file,
        "clean_file": clean_file,
        "chunk_count": len(stored_chunks),
        "chunks": stored_chunks,
    }
