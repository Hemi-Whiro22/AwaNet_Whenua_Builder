from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        expected_bearer = os.getenv(
            "HUMAN_BEARER_KEY") or os.getenv("PIPELINE_TOKEN")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing Bearer token.")

        token = auth_header.split("Bearer ")[1]
        if not expected_bearer or token != expected_bearer:
            raise HTTPException(
                status_code=403, detail="Invalid Bearer token.")

        # Optional: store identity for logging/tracing
        request.state.human_identity = os.getenv("HUMAN_IDENTITY")
        request.state.trace_id = os.getenv("TRACE_ID")

        return await call_next(request)


"""Utility functions for Kitenga tool registration script."""
