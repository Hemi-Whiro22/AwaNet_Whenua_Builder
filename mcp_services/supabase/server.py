#!/usr/bin/env python3
"""
Supabase MCP Server
===================
Supabase database and storage API integration via Model Context Protocol.
CRUD operations, RPC calls, and file storage management.

Env:
  SUPABASE_URL    Supabase project URL (required)
  SUPABASE_KEY    Supabase API key (required)
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class SupabaseServer:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables are required")

        self.base_url = f"{self.url}/rest/v1"
        self.storage_url = f"{self.url}/storage/v1"

        # Load schema and tools
        schema_path = Path(__file__).parent / "schema.json"
        tools_path = Path(__file__).parent / "tools.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        with open(tools_path) as f:
            tools_data = json.load(f)
            self.tools = tools_data.get("tools", [])

    def get_headers(self, storage: bool = False) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        if not storage:
            headers["Prefer"] = "return=representation"
        return headers

    async def call_supabase(
        self,
        method: str,
        path: str,
        base: str = "rest",
        payload: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call Supabase API."""
        base_url = self.base_url if base == "rest" else self.storage_url
        url = f"{base_url}{path}"
        headers = self.get_headers(storage=(base == "storage"))

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, params=query, headers=headers)
                elif method.upper() == "POST":
                    resp = await client.post(url, json=payload, headers=headers, params=query)
                elif method.upper() == "PATCH":
                    resp = await client.patch(url, json=payload, headers=headers, params=query)
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, headers=headers, params=query)
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
    server = Server("supabase")
    supabase = SupabaseServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available Supabase tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in supabase.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a Supabase tool."""

        tool_def = next((t for t in supabase.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        # Tool to Supabase API mapping
        try:
            if name == "supabase_select":
                table = arguments.pop("table")
                path = f"/{table}"
                result = await supabase.call_supabase("GET", path, query=arguments)

            elif name == "supabase_insert":
                table = arguments.pop("table")
                data = arguments.pop("data")
                path = f"/{table}"
                result = await supabase.call_supabase("POST", path, payload=data, query=arguments)

            elif name == "supabase_update":
                table = arguments.pop("table")
                data = arguments.pop("data")
                filters = arguments.pop("filters", {})
                path = f"/{table}"
                # Merge filters into query
                query = {**filters, **arguments}
                result = await supabase.call_supabase("PATCH", path, payload=data, query=query)

            elif name == "supabase_delete":
                table = arguments.pop("table")
                filters = arguments.pop("filters", {})
                path = f"/{table}"
                query = {**filters, **arguments}
                result = await supabase.call_supabase("DELETE", path, query=query)

            elif name == "supabase_rpc":
                function_name = arguments.pop("function_name")
                params = arguments.pop("params", {})
                path = f"/rpc/{function_name}"
                result = await supabase.call_supabase("POST", path, payload=params)

            elif name == "supabase_upload_file":
                bucket_name = arguments.pop("bucket_name")
                file_path = arguments.pop("file_path")
                path = f"/buckets/{bucket_name}/upload"
                result = await supabase.call_supabase("POST", path, base="storage", payload=arguments)

            elif name == "supabase_list_buckets":
                path = "/buckets"
                result = await supabase.call_supabase("GET", path, base="storage")

            else:
                result = {"error": f"Tool {name} not implemented"}

        except Exception as e:
            result = {"error": str(e)}

        return [TextContent(type="text", text=json.dumps(result))]

    return server


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


if __name__ == "__main__":
    asyncio.run(main())
