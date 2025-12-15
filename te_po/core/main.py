from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from te_po.utils.middleware.auth_middleware import BearerAuthMiddleware

from te_po.core.env_loader import load_env, enforce_utf8_locale

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
    kitenga_backend,
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
)
from te_po.utils.middleware.utf8_enforcer import apply_utf8_middleware

# Load environment early for local runs/tests
load_env()
enforce_utf8_locale()

app = FastAPI(
    title="Kitenga Whiro — Māori Intelligence Engine",
    version="1.0.0",
)
app.add_middleware(BearerAuthMiddleware)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
apply_utf8_middleware(app)


@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "kaitiaki": "Kitenga Whiro",
        "message": "Kia ora — intelligence aligned with Māori truth.",
    }


@app.get("/heartbeat", tags=["Health"])
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
app.include_router(kitenga_backend.router)
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


# For local launches only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
