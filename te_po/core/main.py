from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from te_po.routes import intake, reo, vector, status, ocr, research, dev, memory, pipeline, assistant
from te_po.utils.middleware.utf8_enforcer import apply_utf8_middleware

app = FastAPI(
    title="Kitenga Whiro — Māori Intelligence Engine",
    version="1.0.0",
)

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


# For local launches only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000, reload=True)
