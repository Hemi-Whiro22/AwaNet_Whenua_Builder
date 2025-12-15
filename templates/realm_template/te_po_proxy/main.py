"""
Te Pó Proxy - Realm-local backend proxy

This is a thin proxy that forwards requests to the main Te Pó backend.
It does NOT import or depend on Te Pó Python modules.
It reads TE_PO_URL from environment to determine the upstream.
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Load environment
te_po_url = os.getenv("TE_PO_URL", "http://localhost:5000")
bearer_key = os.getenv("BEARER_KEY", "")
realm_id = os.getenv("REALM_ID", "unknown")


def get_cors_origins():
    """Read CORS_ALLOW_ORIGINS from environment or use sensible defaults."""
    env_origins = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    # Defaults for local development
    return [
        "http://localhost:5173",
        "http://localhost:8100",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8100",
    ]


app = FastAPI(
    title=f"Te Pó Proxy - {realm_id}",
    description="Thin proxy to main Te Pó backend"
)

# CORS for realm UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    print(f"[te_po_proxy] Started for realm: {realm_id}")
    print(f"[te_po_proxy] Upstream Te Pó: {te_po_url}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "realm": realm_id,
        "upstream": te_po_url
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str):
    """Proxy all requests to upstream Te Pó."""
    try:
        upstream_url = f"{te_po_url}/{path}"

        headers = {}
        if bearer_key:
            headers["Authorization"] = f"Bearer {bearer_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(upstream_url, headers=headers)
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Upstream error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PROXY_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
