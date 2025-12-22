#!/usr/bin/env python3
"""
OpenAI MCP Server
=================
Wraps the OpenAI Responses API for Kitenga MCP.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime
    OpenAI = None


class OpenAIServer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        self.default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")
        self.schema = self._load_json("schema.json")
        self.tools = self._load_json("tools.json").get("tools", [])

    @staticmethod
    def _load_json(filename: str) -> Dict[str, Any]:
        path = Path(__file__).parent / filename
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _get_client(self) -> Any:
        if OpenAI is None:
            raise RuntimeError("openai package not installed; run pip install openai")
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    @staticmethod
    def _extract_text(response: Any) -> str:
        text = getattr(response, "output_text", None)
        if text is not None:
            return text
        body = []
        output = getattr(response, "output", [])
        for item in output:
            if getattr(item, "type", None) == "output_text":
                body.append(getattr(item, "text", ""))
        return "".join(body)

    async def _to_thread(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    def _responses_generate_sync(self, args: Dict[str, Any]) -> Dict[str, Any]:
        client = self._get_client()
        model = args.get("model") or self.default_model
        payload: Dict[str, Any] = {
            "model": model,
            "input": args["input"],
            "background": bool(args.get("background", False)),
        }
        if instructions := args.get("instructions"):
            payload["instructions"] = instructions
        if tokens := args.get("max_output_tokens"):
            payload["max_output_tokens"] = int(tokens)
        if temperature := args.get("temperature"):
            payload["temperature"] = float(temperature)
        if metadata := args.get("metadata"):
            payload["metadata"] = metadata

        response = client.responses.create(**payload)
        return {
            "id": getattr(response, "id", None),
            "status": getattr(response, "status", None),
            "output_text": self._extract_text(response),
        }

    def _responses_get_sync(self, response_id: str) -> Dict[str, Any]:
        client = self._get_client()
        response = client.responses.retrieve(response_id)
        return {
            "id": getattr(response, "id", None),
            "status": getattr(response, "status", None),
            "output_text": self._extract_text(response),
        }


def create_server() -> Server:
    server = Server("openai")
    openai_service = OpenAIServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name=tool["name"], description=tool.get("description", ""), inputSchema=tool.get("inputSchema", {}))
            for tool in openai_service.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        tool_def = next((t for t in openai_service.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        try:
            if name == "responses_generate":
                result = await openai_service._to_thread(
                    openai_service._responses_generate_sync, arguments
                )
            elif name == "responses_get":
                result = await openai_service._to_thread(
                    openai_service._responses_get_sync, arguments["response_id"]
                )
            else:
                result = {"error": f"Tool {name} not implemented"}
        except KeyError as exc:
            result = {"error": f"Missing argument: {exc.args[0]}"}
        except Exception as exc:  # pragma: no cover - bubble real errors
            result = {"error": str(exc)}

        return [TextContent(type="text", text=json.dumps(result))]

    return server


def create_fastapi_app():
    from fastapi import FastAPI

    mcp_server = create_server()
    app = FastAPI()

    @app.get("/status")
    async def status():
        return {"status": "ok", "service": "openai"}

    app.state.mcp_server = mcp_server
    return app


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_fastapi_app(), host="0.0.0.0", port=0)
