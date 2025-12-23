import base64
import hashlib
import io
import json
import re
import uuid
from typing import Any, Dict, Tuple

from te_po.mauri import MAURI
from te_po.pipeline.cleaner.text_cleaner import clean_text
from te_po.pipeline.chunker.chunk_engine import chunk_text
from te_po.pipeline.embedder.embed_engine import embed_text
from te_po.pipeline.ocr.ocr_engine import run_ocr
from te_po.pipeline.supabase_writer.writer import save_chunk
from te_po.services.local_storage import save, timestamp
from te_po.services.vector_service import push_chunk_embedding
from te_po.services.supabase_service import (
    record_file_metadata,
    upload_bytes,
    detect_content_type,
    log_pipeline_run,
    log_chunks_metadata,
    log_vector_batch,
)
from te_po.utils.openai_client import client as oa_client, DEFAULT_BACKEND_MODEL, generate_text
from te_po.pipeline.metrics import log_memory_usage

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
TEXT_EXT = {".txt", ".md", ".json", ".yaml", ".yml", ".html", ".htm"}
PDF_EXT = {".pdf"}
AUDIO_EXT = {".wav", ".mp3", ".m4a"}


def _extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from PDF using pdfplumber only (fast path).
    OCR fallback is intentionally disabled here to avoid long-running tesseract/image conversions.
    If a PDF is image-only, prefer uploading images directly or add a dedicated OCR path.
    """
    text_parts: list[str] = []
    PAGE_LIMIT = 10  # cap to avoid long-running extraction on huge PDFs

    try:
        import pdfplumber
    except Exception:
        pdfplumber = None

    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    if idx >= PAGE_LIMIT:
                        break
                    extracted = page.extract_text() or ""
                    if extracted.strip():
                        text_parts.append(extracted.strip())
        except Exception:
            pass

    return "\n\n".join(text_parts).strip()


def _persist_raw(
    image_bytes: bytes,
    filename: str | None,
    source: str,
    allow_supabase: bool = True,
) -> Tuple[str, Dict[str, Any], str]:
    safe_name = filename or f"upload_{uuid.uuid4().hex}"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    raw_file = f"{timestamp()}_{safe_name}.b64"
    dest_path = f"{source}/raw/{raw_file}"

    if allow_supabase:
        upload_result = upload_bytes(encoded.encode("utf-8"), dest_path)
    else:
        upload_result = {"status": "skipped", "reason": "taonga_mode", "path": dest_path}

    if upload_result.get("status") == "ok":
        return dest_path, upload_result, encoded

    # Fallback to local persistence when Supabase is unavailable or skipped
    local_path = save("raw", raw_file, encoded)
    fallback_result = dict(upload_result)
    fallback_result.setdefault("path", dest_path)
    fallback_result["fallback_path"] = local_path
    return local_path, fallback_result, encoded


def _persist_clean_text(
    cleaned_text: str,
    source: str,
    allow_supabase: bool = True,
) -> Tuple[str, Dict[str, Any]]:
    clean_file = f"{timestamp()}_{uuid.uuid4().hex}.txt"
    dest_path = f"{source}/clean/{clean_file}"

    if allow_supabase:
        upload_result = upload_bytes(cleaned_text.encode("utf-8"), dest_path)
    else:
        upload_result = {"status": "skipped", "reason": "taonga_mode", "path": dest_path}

    if upload_result.get("status") == "ok":
        return dest_path, upload_result

    local_path = save("clean", clean_file, cleaned_text)
    fallback_result = dict(upload_result)
    fallback_result.setdefault("path", dest_path)
    fallback_result["fallback_path"] = local_path
    return local_path, fallback_result


def _html_to_text(raw: str) -> str:
    """Best-effort HTML to text conversion."""
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(raw, "html.parser")
        return soup.get_text(" ", strip=True)
    except Exception:
        # Fallback: strip tags roughly
        return re.sub(r"<[^>]+>", " ", raw)


def run_pipeline(
    file_bytes: bytes,
    filename: str | None = None,
    source: str = "upload",
    generate_summary: bool = False,
    mode: str | None = None,
    allow_taonga_store: bool = False,
) -> dict[str, Any]:
    log_memory_usage("start of pipeline")

    taonga_restricted = (mode or source) == "taonga" and not allow_taonga_store
    raw_file, raw_upload, raw_encoded = _persist_raw(
        file_bytes,
        filename,
        source,
        allow_supabase=not taonga_restricted,
    )
    name = (filename or "").lower()
    glyph = (
        MAURI.get("identity", {}).get("glyph_id")
        or MAURI.get("openai", {}).get("glyph_id")
        or "unknown"
    )

    log_memory_usage("after raw file persistence")

    # Detect file type and extract text accordingly
    ext = ""
    if "." in name:
        ext = name[name.rfind(".") :]

    ocr_meta_records: list[dict[str, Any]] = []

    if ext in IMAGE_EXT:
        ocr_result = run_ocr(file_bytes, mode=mode or source, apply_encoding=True)
        raw_text = ocr_result.get("protected_text") or ocr_result.get("raw_text") or ""
        # If OCR failed, surface the error text so we don't silently store blanks
        if ocr_result.get("method_used") == "error":
            raw_text = ocr_result.get("raw_text") or raw_text or "[ocr error]"
            summary_result = raw_text
            summary_long = raw_text
        ocr_meta_records.append(
            {
                "method_used": ocr_result.get("method_used"),
                "confidence": ocr_result.get("confidence"),
                "cultural_content": ocr_result.get("cultural_content"),
                "stealth_encoded": ocr_result.get("stealth_encoded"),
                "protected_text": ocr_result.get("protected_text"),
                "protection_metadata": ocr_result.get("metadata"),
            }
        )
    elif ext in TEXT_EXT:
        raw_text = file_bytes.decode("utf-8", errors="ignore")
        if ext in {".html", ".htm"}:
            # OCR any embedded base64 images before stripping HTML
            base64_images = re.findall(r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", raw_text, flags=re.IGNORECASE)
            for b64img in base64_images[:5]:  # cap to avoid overload
                try:
                    img_bytes = base64.b64decode(b64img)
                    ocr_result = run_ocr(img_bytes, mode=mode or source, apply_encoding=True)
                    if ocr_result.get("protected_text"):
                        raw_text += "\n\n" + (ocr_result.get("protected_text") or "")
                    ocr_meta_records.append(
                        {
                            "method_used": ocr_result.get("method_used"),
                            "confidence": ocr_result.get("confidence"),
                            "cultural_content": ocr_result.get("cultural_content"),
                            "stealth_encoded": ocr_result.get("stealth_encoded"),
                            "protected_text": ocr_result.get("protected_text"),
                            "protection_metadata": ocr_result.get("metadata"),
                        }
                    )
                except Exception:
                    continue
            raw_text = _html_to_text(raw_text)
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
    clean_file, clean_upload = _persist_clean_text(
        cleaned,
        source,
        allow_supabase=not taonga_restricted,
    )

    chunks = chunk_text(cleaned)
    meta = {
        "source": source,
        "glyph": glyph,
        "raw_file": raw_file,
        "mode": mode or source,
    }

    stored_chunks = []
    vector_batch_id = None
    for chunk in chunks:
        embedding = embed_text(chunk)
        chunk_record = save_chunk(chunk, embedding, meta)
        chunk_hash = hashlib.sha256(chunk.encode("utf-8", errors="ignore")).hexdigest()
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
                "hash": chunk_hash,
                "remote": remote,
            }
        )
    if not vector_batch_id and isinstance(remote, dict):
        vector_batch_id = remote.get("batch_id")

    log_payload = {
        "event": "pipeline_run",
        "source": source,
        "glyph": meta["glyph"],
        "raw_file": raw_file,
        "clean_file": clean_file,
        "chunks": [c["id"] for c in stored_chunks],
    }
    save(
        "logs",
        f"pipeline_{timestamp()}_{uuid.uuid4().hex}.json",
        json.dumps(
            log_payload,
            indent=2,
        ),
    )

    # Content metadata hashes / content-type
    raw_hash = hashlib.sha256(raw_encoded.encode("utf-8", errors="ignore")).hexdigest()
    clean_hash = hashlib.sha256(cleaned.encode("utf-8", errors="ignore")).hexdigest()
    raw_ct = detect_content_type(filename or "") or "text/plain"
    clean_ct = detect_content_type(clean_file) or "text/plain"

    supabase_uploads = {
        "raw": raw_upload,
        "clean": clean_upload,
    }

    summary_result = None
    summary_long = None
    if generate_summary and oa_client is not None:
        try:
            summary_result = generate_text(
                [
                    {"role": "system", "content": "Summarize the following text succinctly in 3-6 sentences."},
                    {"role": "user", "content": cleaned[:12000]},
                ],
                model=DEFAULT_BACKEND_MODEL,
                max_tokens=500,
            )
            # Longer contextual summary for storage/research
            summary_long = generate_text(
                [
                    {
                        "role": "system",
                        "content": "Provide a richer summary (approx 800-1200 words) capturing key themes, entities, timelines, and locations. Keep it culturally respectful.",
                    },
                    {"role": "user", "content": cleaned[:20000]},
                ],
                model=DEFAULT_BACKEND_MODEL,
                max_tokens=1800,
            )
        except Exception:
            summary_result = None
            summary_long = None

    supabase_meta = record_file_metadata(
        source=source,
        raw_path=raw_file,
        clean_path=clean_file,
        chunks=[c["id"] for c in stored_chunks],
        vector_batch_id=vector_batch_id,
        extra={
            "glyph": meta["glyph"],
            "storage": supabase_uploads,
            "raw_sha256": raw_hash,
            "clean_sha256": clean_hash,
            "raw_content_type": raw_ct,
            "clean_content_type": clean_ct,
            "summary_short": summary_result,
            "summary_long": summary_long,
            "mode": mode or source,
            "ocr": ocr_meta_records if ocr_meta_records else None,
        },
    )

    # Best-effort Supabase logging for pipeline/chunks/vector batch
    log_chunks_metadata(stored_chunks, metadata={"source": source, "glyph": glyph})
    log_pipeline_run(
        source=source,
        status="ok",
        glyph=meta["glyph"],
        raw_file=raw_file,
        clean_file=clean_file,
        chunk_ids=[c["id"] for c in stored_chunks],
        vector_batch_id=vector_batch_id,
        storage=supabase_uploads,
        supabase_status=supabase_meta,
        metadata={"summary_long": summary_long} if summary_long else {},
    )
    if vector_batch_id:
        log_vector_batch(
            batch_id=vector_batch_id,
            vector_store_id=None,
            status=(remote.get("batch_status") if isinstance(remote, dict) else None),
            metadata={"source": source, "glyph": glyph},
        )

    log_memory_usage("end of pipeline")
    return {
        "status": "ok",
        "glyph": meta["glyph"],
        "source": source,
        "raw_file": raw_file,
        "clean_file": clean_file,
        "chunk_count": len(stored_chunks),
        "chunks": stored_chunks,
        "vector_batch_id": vector_batch_id,
        "supabase": supabase_meta,
        "summary": summary_result,
        "summary_long": summary_long,
    }
