import os

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from te_po.stealth_ocr import pipeline_token_hash


class BearerAuthMiddleware(BaseHTTPMiddleware):
    UNPROTECTED_PATHS = {
        "/",
        "/heartbeat",
        "/health",
        "/docs",
        "/openapi.json",
        "/openapi-core.json",
        "/.well-known/openapi-core.json",
        "/gpt_connect.yaml",
        "/realm.json",
        "/assistant/health",
        "/redoc",
        "/state/public",
        "/state/version",
        "/mcp/health",
        "/mcp/tools/list",
        "/mcp/tools/describe",
        "/debug/routes",
        "/analysis/sync-status",
        "/analysis/documents/latest",
        "/openai_tools.json",
    }
    UNPROTECTED_PREFIXES = {"/static"}
    STEALTH_AUTH_PATHS = {"/awa/protocol/event"}
    STEALTH_HEADER = "x-stealth-token-hash"

    async def dispatch(self, request: Request, call_next):
        if request.method in ("OPTIONS", "HEAD"):
            return await call_next(request)

        path = request.url.path
        if path in self.UNPROTECTED_PATHS:
            return await call_next(request)

        for p in self.UNPROTECTED_PREFIXES:
            if path.startswith(p):
                return await call_next(request)

        auth_header = request.headers.get("authorization") or ""
        stealth_header = request.headers.get(self.STEALTH_HEADER)
        expected_bearer = os.getenv("HUMAN_BEARER_KEY") or os.getenv("PIPELINE_TOKEN")
        expected_hash = pipeline_token_hash()

        if not expected_bearer:
            return await call_next(request)

        if (
            path in self.STEALTH_AUTH_PATHS
            and expected_hash
            and stealth_header
            and stealth_header == expected_hash
        ):
            request.state.human_identity = os.getenv("HUMAN_IDENTITY")
            request.state.trace_id = os.getenv("TRACE_ID")
            return await call_next(request)

        if not auth_header.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token.")

        token = auth_header.split(" ", 1)[1].strip()
        if token != expected_bearer:
            raise HTTPException(status_code=403, detail="Invalid Bearer token.")

        request.state.human_identity = os.getenv("HUMAN_IDENTITY")
        request.state.trace_id = os.getenv("TRACE_ID")
        return await call_next(request)

def apply_bearer_middleware(app: ASGIApp) -> None:
    app.add_middleware(BearerAuthMiddleware)
