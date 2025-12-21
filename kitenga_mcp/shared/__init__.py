#!/usr/bin/env python3
"""
MCP Services Shared Utilities
============================
Common functions and utilities for all MCP servers.
"""

import json
import os
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for MCP services."""

    @staticmethod
    def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
        """Get environment variable with optional default."""
        value = os.getenv(key, default)
        if required and not value:
            raise ValueError(f"Required environment variable {key} not set")
        return value

    @staticmethod
    def load_schema(schema_path: str) -> Dict[str, Any]:
        """Load schema JSON file."""
        with open(schema_path) as f:
            return json.load(f)

    @staticmethod
    def load_tools(tools_path: str) -> list[Dict[str, Any]]:
        """Load tools JSON file."""
        with open(tools_path) as f:
            data = json.load(f)
            return data.get("tools", [])


class ContextManager:
    """Manages persistent context across tool calls."""

    def __init__(self):
        self.context = {}
        self.execution_log = []

    def store(self, key: str, value: Any) -> None:
        """Store a value in context."""
        self.context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from context."""
        return self.context.get(key, default)

    def log_execution(self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log a tool execution."""
        self.execution_log.append({
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        })

    def get_execution_history(self) -> list:
        """Get execution history."""
        return self.execution_log


class AuthManager:
    """Manages authentication tokens and headers."""

    @staticmethod
    def get_bearer_headers(token: str, content_type: str = "application/json") -> Dict[str, str]:
        """Get headers with Bearer token."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        }

    @staticmethod
    def get_github_headers(token: str) -> Dict[str, str]:
        """Get headers for GitHub API."""
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }


# Global context manager (shared across all MCP servers)
_global_context = ContextManager()


def get_context() -> ContextManager:
    """Get the global context manager."""
    return _global_context
