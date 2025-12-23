import os
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class BearerAuthMiddleware(BaseHTTPMiddleware):
    UNPROTECTED_PATHS = {
        "/",
        "/heartbeat",
        "/health",
        "/docs",
        "/openapi.json",
        "/gpt_connect.yaml",
        "/realm.json",
        "/assistant/health",
        "/redoc",
        "/state/public",
        "/state/version",
        "/mcp/health",
        "/debug/routes",
    }
    UNPROTECTED_PREFIXES = {"/static"}

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
        expected_bearer = os.getenv("HUMAN_BEARER_KEY") or os.getenv("PIPELINE_TOKEN")

        if not expected_bearer:
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
