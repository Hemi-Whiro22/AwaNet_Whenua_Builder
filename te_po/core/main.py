from datetime import datetime
import httpx
import json
import logging
import os
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Middleware imports
from te_po.utils.middleware.auth_middleware import BearerAuthMiddleware
from te_po.utils.middleware.utf8_enforcer import apply_utf8_middleware

# Sub-app import (Kitenga MCP)
from kitenga_mcp.app_server import app as mcp_app

# Core env + routers
from te_po.core.env_loader import enforce_utf8_locale, get_env
from te_po.core import awa_gpt, awa_realtime
from te_po.routes import (
    intake,
    reo,
    vector,
    status,
    ocr,
    research,
    dev,
    memory,
    pipeline,
    assistant,
    assistant_bridge,
    recall,
    kitenga_backend,
    kitenga_db,
    logs,
    assistants_meta,
    state,
    documents,
    chat,
    cards,
    roshi,
    sell,
    metrics,
    awa_protocol,
    llama3,
    realm_generator,
    cors_manager,
    awa,
)

# -------------------------------------------------------------------
# 🧠 APP INITIALIZATION
# -------------------------------------------------------------------

logger = logging.getLogger("te_po.core.main")

# Create the app once (do NOT redeclare)
app = FastAPI(
    title="Te Pō — Kitenga Whiro Backend",
    version="1.0.0",
    description="Awa Network core backend orchestrator — Māori Intelligence Engine",
    servers=[{"url": "https://tiwhanawhana-backend.onrender.com", "description": "Render deployment"}],
)

# Enforce UTF-8 locale early
enforce_utf8_locale()

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_FILE = REPO_ROOT / "gpt_connect.yaml"
REALM_FILE = REPO_ROOT / "realm.json"
AWA_LOG_URL = os.getenv("AWA_LOG_URL", "https://tiwhanawhana-backend.onrender.com/awa/log")

# -------------------------------------------------------------------
# 🌐 CORS + AUTH MIDDLEWARE
# -------------------------------------------------------------------

def get_cors_origins():
    env_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5000",
        "http://localhost:5001",
        "http://localhost:5173",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5173",
    ]

# Apply middleware (order matters)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(BearerAuthMiddleware)
apply_utf8_middleware(app)

# -------------------------------------------------------------------
# 💚 ROOT + HEALTH ROUTES
# -------------------------------------------------------------------

@app.get("/", tags=["Root"])
@app.head("/", tags=["Root"], include_in_schema=False)
async def root():
    return {
        "status": "online",
        "kaitiaki": "Kitenga Whiro",
        "message": "Kia ora — intelligence aligned with Māori truth.",
    }

@app.get("/heartbeat", tags=["Health"])
@app.head("/heartbeat", tags=["Health"], include_in_schema=False)
async def heartbeat():
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


async def _send_awa_log(path: str, realm: dict):
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            await client.post(
                AWA_LOG_URL,
                json={"path": path, "realm": realm, "event": "schema_access"},
            )
        except Exception as exc:  # pragma: no cover - best-effort logging
            logger.warning("Awa log failed for %s: %s", path, exc)


def _load_realm():
    if not REALM_FILE.exists():
        return {}
    try:
        return json.loads(REALM_FILE.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to load realm.json: %s", exc)
        return {}


@app.get("/gpt_connect.yaml", include_in_schema=False)
async def serve_gpt_connect(background_tasks: BackgroundTasks):
    realm = _load_realm()
    background_tasks.add_task(_send_awa_log, "/gpt_connect.yaml", realm)

    headers = {
        "X-Realm-Name": realm.get("name", "Te Pō Assistant"),
        "X-Realm-Owner": realm.get("realm", "AwaNet"),
        "X-Realm-Version": realm.get("version", "1.0.0"),
    }

    if not SPEC_FILE.exists():
        return JSONResponse({"error": "Spec file not found"}, status_code=404)

    return FileResponse(
        SPEC_FILE,
        media_type="text/yaml; charset=utf-8",
        headers=headers,
    )


@app.get("/realm.json", include_in_schema=False)
async def serve_realm():
    if not REALM_FILE.exists():
        return JSONResponse({"error": "realm.json missing"}, status_code=404)
    return FileResponse(REALM_FILE, media_type="application/json")

# -------------------------------------------------------------------
# 🔗 ROUTER REGISTRATION
# -------------------------------------------------------------------

app.include_router(intake.router)
app.include_router(reo.router)
app.include_router(vector.router)
app.include_router(status.router)
app.include_router(ocr.router)
app.include_router(research.router)
app.include_router(dev.router)
app.include_router(memory.router)
app.include_router(pipeline.router)
app.include_router(assistant.router)
app.include_router(assistant_bridge.router)
app.include_router(recall.router)
app.include_router(kitenga_backend.router)
app.include_router(kitenga_db.router)
app.include_router(logs.router)
app.include_router(assistants_meta.router)
app.include_router(state.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(cards.router)
app.include_router(roshi.router)
app.include_router(sell.router)
app.include_router(metrics.router)
app.include_router(awa_protocol.router)
app.include_router(llama3.router)
app.include_router(realm_generator.router)
app.include_router(cors_manager.router)
app.include_router(awa.router)
app.include_router(awa_gpt.router)
app.include_router(awa_realtime.router)

# -------------------------------------------------------------------
# 🧩 Mount Kitenga MCP as a sub-app
# -------------------------------------------------------------------
app.mount("/mcp", mcp_app)
from te_po.core.awa_event_loop import start_awa_event_loop

@app.on_event("startup")
async def startup_event():
    start_awa_event_loop()

# -------------------------------------------------------------------
# 🧪 DEV ENTRY POINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("✅ Starting Te Pō backend...")
    uvicorn.run("te_po.core.main:app", host="0.0.0.0", port=10000, reload=True)
