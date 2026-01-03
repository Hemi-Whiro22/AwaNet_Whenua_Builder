import os

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from te_po.core.auth import load_tokens, classify_identity, require_token
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
        """
        Enforce bearer auth with explicit identity classification.
        Behaviour is preserved:
        - When no token envs are set, requests pass through (legacy mode).
        - STEALTH_AUTH_PATHS accept the hashed pipeline token via header.
        """
        if request.method in ("OPTIONS", "HEAD"):
            return await call_next(request)

        path = request.url.path
        if path in self.UNPROTECTED_PATHS:
            return await call_next(request)

        for p in self.UNPROTECTED_PREFIXES:
            if path.startswith(p):
                return await call_next(request)

        auth_header = request.headers.get("authorization")
        stealth_header = request.headers.get(self.STEALTH_HEADER)
        tokens = load_tokens()
        expected_hash = pipeline_token_hash()

        # No configured tokens: preserve previous implicit bypass.
        if not tokens.any_active:
            return await call_next(request)

        if (
            path in self.STEALTH_AUTH_PATHS
            and expected_hash
            and stealth_header
            and stealth_header == expected_hash
        ):
            request.state.identity_role = "pipeline-stealth"
            request.state.human_identity = os.getenv("HUMAN_IDENTITY")
            request.state.trace_id = os.getenv("TRACE_ID")
            return await call_next(request)

        # Prefer human token when configured, else pipeline/service for general protection.
        expected = tokens.human or tokens.pipeline or tokens.service
        require_token(auth_header, expected, token_label="global access")

        role, token_used = classify_identity(tokens, auth_header)
        request.state.identity_role = role
        request.state.token_used = token_used
        request.state.human_identity = os.getenv("HUMAN_IDENTITY")
        request.state.trace_id = os.getenv("TRACE_ID")
        return await call_next(request)

def apply_bearer_middleware(app: ASGIApp) -> None:
    app.add_middleware(BearerAuthMiddleware)
