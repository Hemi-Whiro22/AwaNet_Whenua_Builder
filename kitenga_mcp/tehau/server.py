#!/usr/bin/env python3
"""
Te Hau MCP Server
=================
Exposes Te Hau orchestrator endpoints as MCP tools.

Env:
  TE_HAU_BASE_URL   Base URL for Te Hau (default: http://localhost:8000)
  TE_HAU_AUTH_TOKEN Bearer token (optional)
  TE_HAU_TIMEOUT    HTTP timeout seconds (default: 60)
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.path.insert(0, str(Path(__file__).parent.parent))


class TeHauServer:
    def __init__(self):
        self.base_url = os.getenv("TE_HAU_BASE_URL", "http://localhost:8000")
        self.auth_token = os.getenv("TE_HAU_AUTH_TOKEN")
        self.timeout = int(os.getenv("TE_HAU_TIMEOUT", "60"))

        schema_path = Path(__file__).parent / "schema.json"
        tools_path = Path(__file__).parent / "tools.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        with open(tools_path) as f:
            tools_data = json.load(f)
            self.tools = tools_data.get("tools", [])

    def headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.auth_token:
            h["Authorization"] = f"Bearer {self.auth_token}"
        return h

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params, headers=self.headers())
                return {"status": resp.status_code, "data": resp.json() if resp.text else None, "error": None if resp.is_success else resp.text}
        except Exception as exc:
            return {"status": 500, "data": None, "error": str(exc)}

    async def post(self, path: str, payload: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, params=params, headers=self.headers())
                return {"status": resp.status_code, "data": resp.json() if resp.text else None, "error": None if resp.is_success else resp.text}
        except Exception as exc:
            return {"status": 500, "data": None, "error": str(exc)}


def create_server() -> Server:
    server = Server("tehau")
    svc = TeHauServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in svc.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        tool_def = next((t for t in svc.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        if name == "tehau_health":
            res = await svc.get("/health")
            return [TextContent(type="text", text=json.dumps(res))]

        if name == "tehau_pipeline_run":
            payload = arguments.get("payload", {})
            res = await svc.post("/pipeline/run", payload=payload)
            return [TextContent(type="text", text=json.dumps(res))]

        if name == "tehau_vector_search":
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 5)
            res = await svc.post("/vector/search", payload={"query": query, "top_k": top_k})
            return [TextContent(type="text", text=json.dumps(res))]

        if name == "tehau_logs_recent":
            limit = arguments.get("limit", 50)
            res = await svc.get("/logs/recent", params={"limit": limit})
            return [TextContent(type="text", text=json.dumps(res))]

        return [TextContent(type="text", text=json.dumps({"error": f"Unhandled tool {name}"}))]

    return server


if __name__ == "__main__":
    server = create_server()
    stdio_server(server).run()
