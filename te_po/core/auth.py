"""
Auth helpers for Te Pō.

This module clarifies the meaning of the bearer tokens we currently rely on
without changing runtime behaviour. Tokens are still sourced from environment
variables, but the intent of each token is explicit:
- human: interactive caller tokens (HUMAN_BEARER_KEY)
- pipeline: ingest / pipeline guardrail (PIPELINE_TOKEN)
- service: internal service-to-service flows (currently reuse PIPELINE_TOKEN)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

from fastapi import HTTPException, status


HUMAN_TOKEN_ENV = "HUMAN_BEARER_KEY"
PIPELINE_TOKEN_ENV = "PIPELINE_TOKEN"
SERVICE_TOKEN_ENV = "SERVICE_BEARER_KEY"


@dataclass(frozen=True)
class AuthTokens:
    human: Optional[str]
    pipeline: Optional[str]
    service: Optional[str]

    @property
    def any_active(self) -> bool:
        return any([self.human, self.pipeline, self.service])


def load_tokens() -> AuthTokens:
    """
    Load tokens from the environment once for the request lifecycle.
    The pipeline token doubles as a service token when SERVICE_BEARER_KEY
    is unset to preserve current behaviour.
    """
    pipeline = os.getenv(PIPELINE_TOKEN_ENV)
    service = os.getenv(SERVICE_TOKEN_ENV) or pipeline
    return AuthTokens(
        human=os.getenv(HUMAN_TOKEN_ENV),
        pipeline=pipeline,
        service=service,
    )


def _parse_bearer(raw_header: Optional[str]) -> Optional[str]:
    if not raw_header:
        return None
    if not raw_header.lower().startswith("bearer "):
        return None
    return raw_header.split(" ", 1)[1].strip() or None


def require_token(
    raw_header: Optional[str],
    expected: Optional[str],
    *,
    token_label: str,
) -> str:
    """
    Validate an Authorization header against an expected token.
    Returns the token when it matches. Raises HTTP 401/403 when present but invalid.
    If no expected token is configured, the check is bypassed to preserve legacy behaviour.
    """
    if not expected:
        return ""

    token = _parse_bearer(raw_header)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing bearer token for {token_label}.",
        )
    if token != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid bearer token for {token_label}.",
        )
    return token


def classify_identity(tokens: AuthTokens, raw_header: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Determine whether the caller is human, pipeline, or service based on
    the supplied Authorization header. Returns a tuple of (role, token_used).
    """
    token = _parse_bearer(raw_header)
    if token and token == tokens.human:
        return ("human", token)
    if token and token == tokens.pipeline:
        return ("pipeline", token)
    if token and token == tokens.service:
        return ("service", token)
    return ("anonymous", token)


def require_pipeline_or_service(raw_header: Optional[str], tokens: Optional[AuthTokens] = None) -> str:
    """
    Require that the caller is presenting the pipeline/service token.
    Uses pipeline token first, then service token fallback (keeps existing behaviour).
    """
    tokens = tokens or load_tokens()
    expected = tokens.pipeline or tokens.service
    return require_token(raw_header, expected, token_label="pipeline/service")


def require_human(raw_header: Optional[str], tokens: Optional[AuthTokens] = None) -> str:
    """
    Require the human bearer token when configured.
    """
    tokens = tokens or load_tokens()
    return require_token(raw_header, tokens.human, token_label="human")
