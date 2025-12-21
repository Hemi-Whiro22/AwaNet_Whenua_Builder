import os
import httpx
import json
import asyncio
from openai import AsyncOpenAI
from fastapi import APIRouter, Request

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AWA_BACKEND_URL = os.getenv(
    "AWA_BACKEND_URL", "https://tiwhanawhana-backend.onrender.com")
MODEL = os.getenv("GPT_MODEL", "gpt-4o")

awa_tool = {
    "name": "awa_bridge",
    "description": "Send structured commands to the Awa orchestration layer for executing Render, Git, or memory tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "description": "High-level intent (e.g. deploy, list_services, summarise)"},
            "domain": {"type": "string", "description": "Tool domain (e.g. render, git, tepo)"},
            "command": {"type": "string", "description": "Command name (e.g. render_list_services)"},
            "input": {"type": "object", "description": "Input parameters for the tool or pipeline"}
        },
        "required": ["intent"]
    }
}


async def call_awa_bridge(intent: str, domain: str = None, command: str = None, input: dict = None):
    """Calls AwaNet /gpt/bridge with provided orchestration parameters."""
    async with httpx.AsyncClient() as client_http:
        res = await client_http.post(
            f"{AWA_BACKEND_URL}/gpt/bridge",
            headers={"Content-Type": "application/json"},
            json={"intent": intent, "domain": domain,
                  "command": command, "input": input or {}},
        )
        print(f"🌊 AwaBridge response: {res.status_code}")
        try:
            return res.json()
        except Exception:
            return {"error": "Invalid JSON response", "text": res.text}


async def gpt_reason(query: str):
    """Send a GPT request with function calling enabled, connected to the Awa orchestration bridge."""
    messages = [
        {"role": "system", "content": "You are AwaGPT, the guardian and guide of AwaNet and Kitenga systems."},
        {"role": "user", "content": query}
    ]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[{"type": "function", "function": awa_tool}],
        tool_choice="auto"
    )

    result = response.choices[0].message
    if hasattr(result, "tool_calls") and result.tool_calls:
        for call in result.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"🧠 AwaGPT calling {name} → {args}")
            await call_awa_bridge(**args)
    return result


@router.post("/awa/gpt/invoke", tags=["AwaGPT"])
async def awa_gpt_invoke(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        return {"error": "Missing query"}
    result = await gpt_reason(query)
    return {"status": "success", "gpt_result": result}
