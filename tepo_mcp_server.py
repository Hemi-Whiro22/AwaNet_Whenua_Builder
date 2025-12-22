#!/usr/bin/env python3
"""
Te Pō MCP Server (stdio)
========================

Wraps Te Pō HTTP tools (defined in kitenga_mcp/tepo/openai_tools.json) as Model
Context Protocol tools. Each MCP tool proxies a Te Pō REST endpoint so IDEs can
invoke Te Pō capabilities via MCP.

Env:
  TE_PO_BASE_URL (required)          Base URL for Te Pō (e.g. http://localhost:8010)
  PIPELINE_TOKEN  (optional)        Bearer token for tools that need auth
  TEPO_TIMEOUT_SECONDS (optional)   Request timeout in seconds (default: 60)
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


@dataclass(frozen=True)
class AuthConfig:
    header: str
    token_env: str


@dataclass(frozen=True)
class ToolConfig:
    name: str
    description: str
    method: str
    path: str
    input_schema: Dict[str, Any]
    auth: Optional[AuthConfig]


def _load_tool_configs() -> tuple[List[ToolConfig], str]:
    tool_file = Path(__file__).resolve().parent / "kitenga_mcp" / "tepo" / "openai_tools.json"
    if not tool_file.is_file():
        raise FileNotFoundError(f"Tool definition file missing: {tool_file}")

    with tool_file.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    tool_configs: List[ToolConfig] = []
    for entry in data.get("tools", []):
        name = entry.get("name")
        method = entry.get("method")
        path = entry.get("path")
        if not all([name, method, path]):
            # Skip entries (e.g. OpenAI function defs) that are not HTTP-backed.
            continue

        auth_cfg: Optional[AuthConfig] = None
        auth_entry = entry.get("auth")
        if isinstance(auth_entry, dict) and auth_entry.get("type") == "bearer":
            token_env = auth_entry.get("token_env")
            header = auth_entry.get("header", "Authorization")
            if token_env:
                auth_cfg = AuthConfig(header=header, token_env=token_env)

        tool_configs.append(
            ToolConfig(
                name=name,
                description=entry.get("description", ""),
                method=method.upper(),
                path=path,
                input_schema=entry.get("input_schema", {}),
                auth=auth_cfg,
            )
        )

    base_url_env = data.get("base_url_env", "TE_PO_BASE_URL")
    return tool_configs, base_url_env


TOOL_CONFIGS, BASE_URL_ENV = _load_tool_configs()
TOOL_LOOKUP = {tool.name: tool for tool in TOOL_CONFIGS}


def create_tepo_server() -> Server:
    server = Server("tepo")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(name=tool.name, description=tool.description, inputSchema=tool.input_schema)
            for tool in TOOL_CONFIGS
        ]

    async def _to_thread(fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    def _call_tool_sync(tool: ToolConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
        base_url = os.getenv(BASE_URL_ENV, "").strip()
        if not base_url:
            return {"error": f"{BASE_URL_ENV} not configured"}

        timeout = float(os.getenv("TEPO_TIMEOUT_SECONDS", "60") or "60")
        base_url = base_url.rstrip("/")
        url = f"{base_url}{tool.path}"

        headers: Dict[str, str] = {"Accept": "application/json"}
        if tool.auth:
            token = os.getenv(tool.auth.token_env, "").strip()
            if not token:
                return {
                    "error": f"Tool '{tool.name}' requires {tool.auth.token_env} for bearer auth."
                }
            headers[tool.auth.header] = f"Bearer {token}"

        json_payload: Optional[Dict[str, Any]] = None
        params_payload: Optional[Dict[str, Any]] = None

        args = arguments or {}
        if tool.method in {"GET", "DELETE"}:
            params_payload = args
        else:
            json_payload = args

        try:
            response = requests.request(
                method=tool.method,
                url=url,
                headers=headers,
                params=params_payload,
                json=json_payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            return {
                "error": f"HTTP request failed for tool '{tool.name}'",
                "details": str(exc),
            }

        try:
            parsed = response.json()
        except ValueError:
            parsed = None

        if response.ok:
            if parsed is not None:
                return parsed
            return {"status": response.status_code, "body": response.text}

        error_payload: Dict[str, Any] = {
            "error": f"Request failed for tool '{tool.name}'",
            "status": response.status_code,
        }
        if parsed is not None:
            error_payload["body"] = parsed
        else:
            error_payload["body"] = response.text
        return error_payload

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        tool = TOOL_LOOKUP.get(name)
        if not tool:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
                )
            ]

        result = await _to_thread(_call_tool_sync, tool, arguments or {})
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]

    return server


async def main() -> None:
    server = create_tepo_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
