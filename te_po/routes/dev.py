from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from te_po.pipeline.chunker.chunk_engine import chunk_text
from te_po.pipeline.cleaner.text_cleaner import clean_text
from te_po.pipeline.ocr.ocr_engine import run_ocr
from te_po.services.local_storage import save, load
from te_po.services.summary_service import summarize_text
from te_po.utils.openai_client import client, generate_text
from te_po.utils.ollama_client import generate_llama_response
from te_po.core.config import settings

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
        res = generate_text(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Summarise this document snippet:\n{chunk}"}],
        )
        results.append(res)
    save("openai", "openai_results.txt", "\n\n".join(results))
    return {"openai": results}


@router.post("/summarise")
def dev_summarise(text: str = Form(...), mode: str = Form("research")):
    summary = summarize_text(text, mode=mode)
    return summary


@router.post("/ollama")
def dev_ollama(
    prompt: str = Form(...),
    system_prompt: str = Form("You are a helpful Māori research assistant."),
    model: str = Form(None),
):
    """Quick chat endpoint for the local Ollama (Llama 3) runtime."""
    try:
        reply = generate_llama_response(prompt=prompt, system_prompt=system_prompt, model=model)
        return {
            "model": model or settings.ollama_model,
            "prompt": prompt,
            "reply": reply,
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc


@router.get("/routes")
def list_routes():
    """List all registered routes in the application."""
    from te_po.core.main import app
    
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods - {"HEAD", "OPTIONS"}) if route.methods else [],
                "name": route.name,
                "tags": getattr(route, "tags", []),
            })
    
    # Group by prefix
    grouped = {}
    for r in routes:
        prefix = r["path"].split("/")[1] if "/" in r["path"] and len(r["path"].split("/")) > 1 else "root"
        if prefix not in grouped:
            grouped[prefix] = []
        grouped[prefix].append(r)
    
    return {
        "total_routes": len(routes),
        "grouped": grouped,
        "routes": routes,
    }


@router.get("/kitenga-status")
def kitenga_status():
    """Get Kitenga Whiro configuration status."""
    from te_po.core.settings_loader import get_cached_settings
    
    try:
        settings = get_cached_settings()
        return {
            "name": settings.name,
            "role": settings.role,
            "glyph": settings.glyph,
            "purpose": settings.purpose,
            "tools_count": len(settings.tools),
            "tools": settings.tools,
            "api_paths": settings.api_paths,
            "features": {
                "taonga_mode": settings.features.taonga_mode,
                "offline": settings.features.offline,
            },
            "openai_configured": bool(settings.openai.assistant_id),
            "supabase_configured": bool(settings.supabase.url),
            "cloudflare_configured": bool(settings.cloudflare.tunnel_name),
        }
    except Exception as exc:
        return {"error": str(exc), "loaded": False}
