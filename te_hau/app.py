import json
from pathlib import Path

import requests
from fastapi import FastAPI, File, HTTPException, Request, UploadFile

from te_hau.services.awa_bus import emit, latest
from te_hau.services.tepo_api import MAURI, te_po_get, te_po_post, te_po_request
from te_hau.services.kaitiaki_store import list_kaitiaki, save_kaitiaki
from shared.awa_bus.awa_events import AwaEvent

app = FastAPI(title="Te Hau API Bridge", version="1.0.0")

MAURI_PATH = Path("/mauri/global_env.json")
MAURI.update(json.loads(MAURI_PATH.read_text()) if MAURI_PATH.exists() else {})


@app.get("/api/status")
def status():
    """Mirror Te Pō status via Te Hau."""
    result = te_po_get("/status")
    emit(AwaEvent(realm="te_hau", type="status", payload=result))
    return result


@app.post("/api/ocr")
async def ocr_proxy(file: UploadFile = File(...)):
    """Proxy OCR requests to Te Pō."""
    result = te_po_post("/ocr/scan", files={"file": (file.filename, await file.read())})
    emit(AwaEvent(realm="te_hau", type="ocr", payload={"file": file.filename, "saved": result.get("saved")}))
    return result


@app.get("/api/kaitiaki")
def kaitiaki_list():
    return list_kaitiaki()


@app.post("/api/kaitiaki")
def kaitiaki_create(payload: dict):
    result = save_kaitiaki(payload)
    emit(AwaEvent(realm="te_hau", type="kaitiaki_create", payload=result))
    return result


@app.get("/api/events")
def events():
    return latest()


@app.post("/api/events")
def push(event: dict):
    evt = AwaEvent(**event)
    emit(evt)
    return {"ok": True}


@app.api_route("/api/{full_path:path}", methods=["GET", "POST"])
async def proxy(full_path: str, request: Request):
    """Generic passthrough so Te Ao can reach Te Pō via Te Hau."""
    path = f"/{full_path}"
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    try:
        if request.method == "GET":
            resp = te_po_request("GET", path, headers=headers, params=request.query_params)
        else:
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                payload = await request.json()
                resp = te_po_request(
                    "POST", path, json=payload, headers=headers, params=request.query_params
                )
            else:
                body = await request.body()
                resp = te_po_request("POST", path, data=body, headers=headers, params=request.query_params)
        emit(AwaEvent(realm="te_hau", type="proxy", payload={"path": path, "status": resp.status_code}))
        return resp.json() if resp.content else {}
    except requests.HTTPError as exc:  # noqa: PERF203
        response = exc.response
        status_code = response.status_code if response is not None else 500
        detail = response.text if response is not None else str(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except requests.RequestException as exc:  # noqa: PERF203
        raise HTTPException(status_code=502, detail=str(exc)) from exc
