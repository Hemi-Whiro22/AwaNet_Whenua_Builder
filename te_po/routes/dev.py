from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from te_po.pipeline.chunker.chunk_engine import chunk_text
from te_po.pipeline.cleaner.text_cleaner import clean_text
from te_po.pipeline.ocr.ocr_engine import run_ocr
from te_po.services.local_storage import save, load
from te_po.services.summary_service import summarize_text
from te_po.utils.openai_client import client

router = APIRouter(prefix="/dev", tags=["Dev"])


@router.post("/ocr")
async def dev_ocr(file: UploadFile = File(...)):
    raw = await file.read()
    text = run_ocr(raw)
    save("raw", "latest_raw.txt", text)
    return {"ocr": text}


@router.get("/clean")
def dev_clean():
    text = load("raw", "latest_raw.txt")
    if text is None:
        raise HTTPException(status_code=400, detail="No raw text to clean. Run OCR first.")
    cleaned = clean_text(text)
    save("clean", "latest_clean.txt", cleaned)
    return {"clean": cleaned}


@router.get("/chunk")
def dev_chunk():
    text = load("clean", "latest_clean.txt")
    if text is None:
        raise HTTPException(status_code=400, detail="No cleaned text available. Run clean first.")
    chunks = chunk_text(text)
    save("chunks", "latest_chunks.json", "\n".join(chunks))
    return {"chunks": chunks}


@router.get("/openai")
def dev_openai():
    if client is None:
        raise HTTPException(status_code=400, detail="OpenAI client not configured.")
    blob = load("chunks", "latest_chunks.json")
    if not blob:
        raise HTTPException(status_code=400, detail="No chunk data available. Run chunk first.")
    chunks = [c for c in blob.split("\n") if c.strip()]
    results = []
    for chunk in chunks:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": f"Summarise this document snippet:\n{chunk}"}],
        )
        results.append(res.output_text.strip())
    save("openai", "openai_results.txt", "\n\n".join(results))
    return {"openai": results}


@router.post("/summarise")
def dev_summarise(text: str = Form(...), mode: str = Form("research")):
    summary = summarize_text(text, mode=mode)
    return summary
