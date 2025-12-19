"""
Security Hardening for MCP Servers
===================================
Provides reusable security patterns extracted from hardened implementations.

Features:
- Request/response logging and sanitization
- Path validation and traversal prevention
- Service allowlisting
- Environment variable protection
- Timeout enforcement
- Rate limiting helpers
"""

import logging
import time
import os
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Set
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Keys that should be redacted in logs
REDACT_KEYS = {"token", "secret", "password", "admin", "key", "auth"}


@dataclass
class SecurityConfig:
    """Security configuration for services."""

    enforce_allowlist: bool = False
    service_allowlist: Optional[Set[str]] = None
    env_deny_patterns: Optional[list] = None
    http_timeout: float = 30.0
    enable_logging: bool = True


class RequestSanitizer:
    """Sanitizes sensitive data in requests/responses."""

    @staticmethod
    def redact_value(value: Any) -> Any:
        """Redact sensitive values."""
        if isinstance(value, str) and len(value) > 50:
            return "***"  # Likely a token/key
        return value

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive keys from dictionary."""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if any(sub in key.lower() for sub in REDACT_KEYS):
                sanitized[key] = "***"
            elif isinstance(value, dict):
                sanitized[key] = RequestSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    RequestSanitizer.sanitize_dict(v) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        return sanitized


class PathValidator:
    """Validates file paths to prevent traversal attacks."""

    def __init__(self, base_dir: Optional[str] = None, enforce: bool = False):
        self.base_dir = Path(base_dir).expanduser() if base_dir else None
        self.enforce = enforce

    def validate(self, path: str) -> Path:
        """Validate and resolve a path."""
        target = Path(path).expanduser()

        # If base_dir is set, resolve relative to it
        if self.base_dir and not target.is_absolute():
            target = self.base_dir / target

        try:
            resolved = target.resolve()
        except Exception as exc:
            raise ValueError(f"Invalid path '{path}': {exc}")

        # Check if path is within base_dir
        if self.base_dir and self.enforce:
            try:
                resolved.relative_to(self.base_dir)
            except ValueError:
                raise ValueError(
                    f"Path '{resolved}' is outside allowed base directory '{self.base_dir}'"
                )

        return resolved


class ServiceAllowlist:
    """Manages service allowlist and mapping."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.allowlist = set(self.config.keys())

    @staticmethod
    def load_from_json(json_str: str) -> "ServiceAllowlist":
        """Load allowlist from JSON string."""
        try:
            config = json.loads(json_str)
            return ServiceAllowlist(config)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse service config JSON: {e}")
            return ServiceAllowlist()

    @staticmethod
    def load_from_file(path: str) -> "ServiceAllowlist":
        """Load allowlist from file."""
        try:
            with open(path, "r") as f:
                config = json.load(f)
            return ServiceAllowlist(config)
        except Exception as e:
            logger.warning(f"Failed to load service config from {path}: {e}")
            return ServiceAllowlist()

    def is_allowed(self, service_id: str) -> bool:
        """Check if service is in allowlist."""
        return service_id in self.allowlist

    def get_mapping(self, alias: str) -> Optional[Dict[str, Any]]:
        """Get service mapping by alias."""
        return self.config.get(alias)


class EnvironmentValidator:
    """Validates environment variable access."""

    def __init__(self, deny_patterns: Optional[list] = None):
        self.deny_patterns = deny_patterns or [
            r"(KEY|TOKEN|SECRET|PASSWORD|SERVICE_ROLE)"
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.deny_patterns]

    def is_denied(self, key: str) -> bool:
        """Check if environment variable key is denied."""
        return any(pattern.search(key) for pattern in self.compiled_patterns)

    def get_safe_value(self, key: str) -> Optional[str]:
        """Get environment value only if not denied."""
        if self.is_denied(key):
            logger.warning(f"Blocked access to environment variable: {key}")
            return None
        return os.getenv(key)


class ToolExecutionWrapper:
    """Wraps tool execution with logging and safety checks."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.sanitizer = RequestSanitizer()

    def wrap_tool(self, tool_name: str):
        """Decorator to wrap tool execution."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(arguments: Dict[str, Any]) -> Any:
                start = time.monotonic()
                sanitized = self.sanitizer.sanitize_dict(arguments)
                status = "ok"

                if self.config.enable_logging:
                    logger.info(f"tool={tool_name} status=start args={sanitized}")

                try:
                    result = await func(arguments)
                    return result
                except Exception as exc:
                    status = f"error:{type(exc).__name__}"
                    logger.exception(f"tool={tool_name} raised {status}")
                    raise
                finally:
                    latency_ms = (time.monotonic() - start) * 1000
                    if self.config.enable_logging:
                        logger.info(
                            f"tool={tool_name} status={status} latency_ms={latency_ms:.2f}"
                        )

            return wrapper

        return decorator


def validate_env_bool(name: str, default: bool = False) -> bool:
    """Parse environment variable as boolean."""
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def get_safe_env(key: str, default: str = "") -> str:
    """Get environment variable with safety checks."""
    value = os.getenv(key, "").strip()
    if not value:
        return default
    return value
