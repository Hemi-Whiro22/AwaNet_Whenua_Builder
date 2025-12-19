#!/usr/bin/env python3
"""
Te Pō MCP Server
================
Exposes Te Pō backend API as Model Context Protocol tools.
Maintains permanent schema context to prevent drops.

Features:
- API endpoint calls to Te Pō backend
- Memory management (store, search, query)
- Pipeline orchestration (job queue, status)
- Full context persistence via schema

Env:
  TE_PO_BASE_URL      Base URL for Te Pō (required)
  TE_PO_AUTH_TOKEN    Bearer token (optional)
  TE_PO_TIMEOUT       HTTP timeout (default: 60)
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.memory import memory, pipeline
from shared.macrons import macronize_value


class TePōServer:
    def __init__(self):
        self.base_url = os.getenv("TE_PO_BASE_URL", "http://localhost:8010")
        self.auth_token = os.getenv("TE_PO_AUTH_TOKEN")
        self.timeout = int(os.getenv("TE_PO_TIMEOUT", "60"))

        # Load schema and tools
        schema_path = Path(__file__).parent / "schema.json"
        tools_path = Path(__file__).parent / "tools.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        with open(tools_path) as f:
            tools_data = json.load(f)
            self.tools = tools_data.get("tools", [])

    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def call_tepo(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call Te Pō endpoint and return result."""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, params=query, headers=headers)
                elif method.upper() == "POST":
                    resp = await client.post(url, json=payload, params=query, headers=headers)
                elif method.upper() == "PUT":
                    resp = await client.put(url, json=payload, params=query, headers=headers)
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, params=query, headers=headers)
                else:
                    return {"error": f"Unsupported method: {method}"}

                return {
                    "status": resp.status_code,
                    "data": resp.json() if resp.text else None,
                    "error": None if resp.is_success else f"HTTP {resp.status_code}",
                }
        except Exception as e:
            return {"status": 500, "data": None, "error": str(e)}


def create_server() -> Server:
    server = Server("tepo")
    tepo = TePōServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available Te Pō tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in tepo.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a Te Pō tool."""

        # Find the tool definition
        tool_def = next((t for t in tepo.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        # Handle memory tools (local)
        if name == "tepo_memory_store":
            realm = arguments.get("realm", "te_ao")
            content = arguments.get("content", "")
            tapu_level = arguments.get("tapu_level", 0)
            result = memory.store_fragment(realm, content, tapu_level)
            result = macronize_value(result)
            return [TextContent(type="text", text=json.dumps(result))]

        if name == "tepo_memory_query":
            realm = arguments.get("realm", "te_ao")
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 3)
            matches = memory.search_memory(realm, query, top_k)
            result = macronize_value({"query": query, "realm": realm, "matches": matches})
            return [TextContent(type="text", text=json.dumps(result))]

        if name == "tepo_memory_list":
            realm = arguments.get("realm", "te_ao")
            memories = memory.get_realm_memories(realm)
            result = macronize_value({"realm": realm, "memories": memories})
            return [TextContent(type="text", text=json.dumps(result))]

        # Handle pipeline tools (local)
        if name == "tepo_pipeline_enqueue":
            realm = arguments.get("realm", "te_ao")
            payload = arguments.get("payload", {})
            priority = arguments.get("priority", 0)
            job = pipeline.enqueue_job(realm, payload, priority)
            return [TextContent(type="text", text=json.dumps(job))]

        if name == "tepo_pipeline_status":
            job_id = arguments.get("job_id")
            job = pipeline.get_job(job_id)
            if not job:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Job {job_id} not found"})
                )]
            return [TextContent(type="text", text=json.dumps(job))]

        if name == "tepo_pipeline_list":
            realm = arguments.get("realm", "te_ao")
            limit = arguments.get("limit", 5)
            jobs = pipeline.get_recent_jobs(realm, limit)
            result = macronize_value({"realm": realm, "jobs": jobs})
            return [TextContent(type="text", text=json.dumps(result))]

        if name == "tepo_pipeline_pending":
            realm = arguments.get("realm", "te_ao")
            jobs = pipeline.get_pending_jobs(realm)
            result = macronize_value({"realm": realm, "pending": jobs})
            return [TextContent(type="text", text=json.dumps(result))]

        # Map tool names to Te Pō backend endpoints and methods
        tool_map = {
            "tepo_kitenga_whisper": ("POST", "/kitenga/gpt-whisper"),
            "tepo_vector_search": ("POST", "/vector/search"),
            "tepo_ocr_scan": ("POST", "/ocr/scan"),
            "tepo_pipeline_run": ("POST", "/awa/pipeline"),
            "tepo_reo_translate": ("POST", "/reo/translate"),
            "tepo_kaitiaki_register": ("POST", "/awa/kaitiaki/register"),
            "tepo_task_execute": ("POST", "/awa/task"),
            "tepo_db_chat_history": ("GET", "/kitenga/db/chat/history/{session_id}"),
            "tepo_db_taonga_search": ("POST", "/kitenga/db/taonga/search"),
            "tepo_health_check": ("GET", "/heartbeat"),
            "tepo_list_kaitiaki": ("GET", "/awa/kaitiaki"),
        }

        if name not in tool_map:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Tool {name} not mapped to endpoint"})
            )]

        method, endpoint = tool_map[name]

        # Handle path parameters
        if "{session_id}" in endpoint and "session_id" in arguments:
            endpoint = endpoint.format(session_id=arguments.pop("session_id"))

        # Call Te Pō backend
        result = await tepo.call_tepo(method, endpoint, payload=arguments)
        result = macronize_value(result)

        return [TextContent(type="text", text=json.dumps(result))]

    return server


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


if __name__ == "__main__":
    asyncio.run(main())
