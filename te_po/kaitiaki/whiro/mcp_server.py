"""
Whiro MCP server (stdio) for Te Pō.

Runs without importing te_po.core.main to keep runtime and tooling separated.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from te_po.kaitiaki.whiro import tools, prompts


TOOL_MAP = {
    "tepo_status": tools.get_status,
    "tepo_pipeline_text": tools.run_pipeline_from_text,
    "tepo_kitenga_ask": tools.kitenga_ask,
}


def create_server() -> Server:
    server = Server("whiro-te-po")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name=name,
                description=f"Whiro tool '{name}' (Te Pō)",
                inputSchema={"type": "object"},
            )
            for name in TOOL_MAP
        ]

    async def _to_thread(fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        fn = TOOL_MAP.get(name)
        if not fn:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
                )
            ]
        try:
            result = await _to_thread(fn, **(arguments or {}))
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]

    return server


async def main() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
