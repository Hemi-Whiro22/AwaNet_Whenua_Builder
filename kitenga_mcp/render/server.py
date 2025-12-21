#!/usr/bin/env python3
"""
Render MCP Server
=================
Render deployment API integration via Model Context Protocol.
Deploy, scale, monitor, and manage services on Render.

Env:
  RENDER_API_KEY    Render API key (required)
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class RenderServer:
    def __init__(self):
        self.base_url = "https://api.render.com/v1"
        self.api_key = os.getenv("RENDER_API_KEY")

        if not self.api_key:
            raise ValueError("RENDER_API_KEY environment variable is required")

        # Load schema and tools
        schema_path = Path(__file__).parent / "schema.json"
        tools_path = Path(__file__).parent / "tools.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        with open(tools_path) as f:
            tools_data = json.load(f)
            self.tools = tools_data.get("tools", [])

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def call_render(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call Render API."""
        url = f"{self.base_url}{path}"
        headers = self.get_headers()

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, params=query, headers=headers)
                elif method.upper() == "POST":
                    resp = await client.post(url, json=payload, headers=headers)
                elif method.upper() == "PUT":
                    resp = await client.put(url, json=payload, headers=headers)
                elif method.upper() == "PATCH":
                    resp = await client.patch(url, json=payload, headers=headers)
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, headers=headers)
                else:
                    return {"error": f"Unsupported method: {method}"}

                data = resp.json() if resp.text else None

                return {
                    "status": resp.status_code,
                    "data": data,
                    "error": None if resp.is_success else resp.text,
                }
        except Exception as e:
            return {"status": 500, "data": None, "error": str(e)}


def create_server() -> Server:
    server = Server("render")
    render = RenderServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available Render tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in render.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a Render tool."""

        tool_def = next((t for t in render.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        # Tool to Render API mapping
        tool_map = {
            "render_list_services": ("GET", "/services"),
            "render_get_service": ("GET", "/services/{service_id}"),
            "render_deploy": ("POST", "/services/{service_id}/deploys"),
            "render_list_deploys": ("GET", "/services/{service_id}/deploys"),
            "render_get_deploy": ("GET", "/services/{service_id}/deploys/{deploy_id}"),
            "render_update_env": ("PUT", "/services/{service_id}/env-groups"),
            "render_list_events": ("GET", "/services/{service_id}/events"),
            "render_scale_service": ("PATCH", "/services/{service_id}"),
        }

        if name not in tool_map:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not mapped"}))]

        method, path_template = tool_map[name]

        # Format path with arguments
        path = path_template
        for key, value in list(arguments.items()):
            placeholder = "{" + key + "}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
                if method != "PATCH" or key != "num_instances":
                    arguments.pop(key)

        # Prepare payload/query based on method
        payload = None
        query = None

        if method == "GET":
            query = arguments
        else:
            payload = arguments

        result = await render.call_render(method, path, payload=payload, query=query)

        return [TextContent(type="text", text=json.dumps(result))]

    return server

def create_fastapi_app():
    mcp_server = create_server()
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/status")
    async def status():
        return {"status": "ok", "service": "render"}

    app.state.mcp_server = mcp_server
    return app


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


if __name__ == "__main__":
    asyncio.run(main())
