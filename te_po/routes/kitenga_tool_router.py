# kitenga_tool_router.py
# Dynamically routes tool calls using your `openai_tools.json`
# Assumes FastAPI backend, Kitenga assistant agent, and vector store are already configured.

import os
import json
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import httpx

router = APIRouter()

# Load tool config
TOOLS_PATH = Path(__file__).resolve().parents[1] / "openai_tools.json"
TOOL_REGISTRY = []

if TOOLS_PATH.exists():
    try:
        with TOOLS_PATH.open() as f:
            TOOL_REGISTRY = json.load(f).get("tools", [])
    except Exception as e:
        print(f"Warning: Could not load openai_tools.json: {e}")
else:
    print(f"Warning: openai_tools.json not found at {TOOLS_PATH} (expected in production)")

# Utility to route tool calls
async def call_tool_endpoint(path: str, method: str, payload: Dict[str, Any], auth_env: str = None):
    base_url = os.getenv("TE_PO_BASE_URL", "http://localhost:10000")
    url = base_url + path
    headers = {"Content-Type": "application/json"}

    if auth_env:
        token = os.getenv(auth_env)
        if not token:
            raise HTTPException(500, detail=f"Missing token for {auth_env}")
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient() as client:
        if method == "POST":
            resp = await client.post(url, json=payload, headers=headers)
        elif method == "GET":
            resp = await client.get(url, params=payload, headers=headers)
        else:
            raise HTTPException(405, detail="Unsupported method")

    return resp.json()

# Dynamic endpoint to handle tool calls
class ToolCall(BaseModel):
    tool_name: str
    payload: Dict[str, Any]

@router.post("/tools/run")
async def run_tool(call: ToolCall):
    for tool in TOOL_REGISTRY:
        if tool.get("name") == call.tool_name or tool.get("function", {}).get("name") == call.tool_name:
            method = tool.get("method", "POST")
            path = tool.get("path")
            auth = tool.get("auth", {})
            auth_env = auth.get("token_env") if auth else None
            return await call_tool_endpoint(path, method, call.payload, auth_env)

    raise HTTPException(404, detail=f"Tool '{call.tool_name}' not found")

# Optional: expose full tool list
@router.get("/tools/list")
async def list_tools():
    return {"tools": TOOL_REGISTRY}
