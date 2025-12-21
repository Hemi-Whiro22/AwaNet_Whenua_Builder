from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from te_po.utils.middleware.auth_middleware import BearerAuthMiddleware
from kitenga_mcp.app_server import app as mcp_app


from te_po.core.env_loader import enforce_utf8_locale, get_env
from te_po.core import awa_gpt  # Import the new AwaGPT router

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
    awa,  # <-- Add this line to include the new awa router
)
from te_po.utils.middleware.utf8_enforcer import apply_utf8_middleware


# Enforce UTF-8 locale early for local runs/tests
enforce_utf8_locale()


def get_cors_origins():
    """
    Read CORS_ALLOW_ORIGINS from environment as comma-separated list.
    Fallback to sensible defaults for local development.

    Example env:
        CORS_ALLOW_ORIGINS=http://localhost:5173,http://example.com,https://example.com
    """
    env_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]

    # Fallback defaults for local development
    return [
        "http://localhost:5000",
        "http://localhost:5001",
        "http://localhost:5173",
        "http://localhost:8100",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8100",
    ]


app = FastAPI(
    title="Kitenga Whiro — Māori Intelligence Engine",
    version="1.0.0",
)

# Middleware order matters: add in reverse order of desired execution
# 1. UTF8 enforcer (runs after auth/CORS checks)
apply_utf8_middleware(app)

# 2. Bearer auth (runs after CORS, but auth checks happen before body processing)
app.add_middleware(BearerAuthMiddleware)

# 3. CORS (outermost, runs first - allows preflight OPTIONS to reach auth middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


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


# ROUTES
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
app.include_router(recall.router)
app.include_router(kitenga_backend.router)
app.include_router(kitenga_db.router)  # Kitenga schema database routes
app.include_router(logs.router)
app.include_router(assistants_meta.router)
app.include_router(state.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(cards.router)
app.include_router(roshi.router)
app.include_router(sell.router)
app.include_router(metrics.router)
app.include_router(awa_protocol.router)  # Model Context Protocol routes
app.include_router(llama3.router)  # Llama3 local inference routes
app.include_router(realm_generator.router)  # Realm spawner routes
app.include_router(cors_manager.router)  # Dynamic CORS management
app.include_router(awa.router)  # <-- Add this line to register the awa router
app.include_router(awa_gpt.router)  # Register the AwaGPT router

# Mount the Kitenga MCP sub-application under /mcp
app.mount("/mcp", mcp_app)


# For local launches only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
