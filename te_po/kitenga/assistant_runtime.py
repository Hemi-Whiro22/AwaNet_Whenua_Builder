"""
Helper utilities for Kitenga assistant interactions.

This module keeps orchestration logic out of FastAPI route handlers while
preserving current behaviour and dependencies on OpenAI and tool registry.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from te_po.routes.kitenga_tool_router import TOOL_REGISTRY, call_tool_endpoint


def extract_message_text(message) -> str:
    parts: List[str] = []
    for block in getattr(message, "content", []) or []:
        block_type = getattr(block, "type", None)
        if block_type == "text" and hasattr(block, "text"):
            value = getattr(block.text, "value", "")
            if value:
                parts.append(value)
        elif hasattr(block, "value") and isinstance(block.value, str):
            parts.append(block.value)
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def find_tool_entry(name: str) -> Optional[Dict[str, Any]]:
    name = name or ""
    for entry in TOOL_REGISTRY:
        if entry.get("name") == name:
            return entry
        function_def = entry.get("function") or {}
        if function_def.get("name") == name:
            return entry
    return None


def tool_output_string(data: Any) -> str:
    try:
        return json.dumps(data, default=str)
    except Exception:
        return json.dumps({"output": str(data)})


async def execute_tool_call(tool_call) -> Dict[str, Any]:
    name = getattr(getattr(tool_call, "function", None), "name", "")
    raw_args = getattr(getattr(tool_call, "function", None), "arguments", "{}")
    try:
        parsed_args = json.loads(raw_args or "{}")
    except Exception:
        parsed_args = {}

    entry = find_tool_entry(name)
    if entry and entry.get("path"):
        method = entry.get("method", "POST")
        auth = entry.get("auth") or {}
        token_env = auth.get("token_env") if isinstance(auth, dict) else None
        try:
            result = await call_tool_endpoint(entry["path"], method, parsed_args, token_env)
            return {"status": "ok", "tool": name, "result": result}
        except HTTPException as exc:
            return {"status": "error", "tool": name, "reason": exc.detail}
        except Exception as exc:
            return {"status": "error", "tool": name, "reason": str(exc)}
    return {"status": "error", "tool": name, "reason": "tool not configured"}


async def poll_assistant_run(
    async_openai_client,
    thread_id: str,
    run_id: str,
) -> Tuple[Any, List[Dict[str, Any]]]:
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")
    tool_history: List[Dict[str, Any]] = []
    for _ in range(180):
        run = await async_openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )
        status = getattr(run, "status", "unknown")
        if status == "completed":
            return run, tool_history
        if status == "requires_action" and getattr(run, "required_action", None):
            tool_calls = getattr(run.required_action.submit_tool_outputs, "tool_calls", []) or []
            outputs = []
            for call in tool_calls:
                payload = await execute_tool_call(call)
                tool_history.append(payload)
                outputs.append(
                    {
                        "tool_call_id": getattr(call, "id", uuid.uuid4().hex),
                        "output": tool_output_string(payload),
                    }
                )
            if outputs:
                await async_openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=outputs,
                )
        elif status in {"failed", "cancelled", "expired"}:
            raise HTTPException(status_code=500, detail=f"Assistant run {status}")
        await asyncio.sleep(1)
    raise HTTPException(status_code=504, detail="Assistant run timeout")


async def latest_assistant_message(async_openai_client, thread_id: str):
    if async_openai_client is None:
        raise HTTPException(status_code=503, detail="Async OpenAI client not configured.")
    messages = await async_openai_client.beta.threads.messages.list(thread_id=thread_id, limit=5)
    for msg in getattr(messages, "data", []) or []:
        if getattr(msg, "role", "") == "assistant":
            return msg
    return messages.data[0] if getattr(messages, "data", None) else None
