from fastapi import APIRouter, Request
import httpx
import os
import uuid
import datetime

router = APIRouter(prefix="/awa", tags=["Awa ↔ Kitenga Bridge"])

KITENGA_URL = os.getenv("KITENGA_MCP_URL", "http://127.0.0.1:8000")
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


@router.get("/bridge/test")
async def bridge_test():
    """Ping Kitenga MCP health from Te Pō."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{KITENGA_URL}/mcp/health")
    return {
        "awa_status": "ok",
        "kitenga_status": r.json(),
    }


@router.post("/awa/orchestrate")
async def awa_orchestrate(request: Request):
    """Orchestrate a full Awa → Kitenga tool/pipeline execution."""
    data = await request.json()
    trace_id = str(uuid.uuid4())
    intent = data.get("intent", "auto")
    domain = data.get("domain")
    command = data.get("command")
    input_payload = data.get("input", {})
    pipeline = data.get("pipeline")
    memory = data.get("memory", True)

    results = {"trace_id": trace_id, "intent": intent, "steps": []}

    async with httpx.AsyncClient() as client:
        # 1️⃣ Optional: Run a pipeline
        if pipeline:
            try:
                res = await client.post(
                    f"{KITENGA_URL}/mcp/tools/call",
                    headers={
                        "Authorization": f"Bearer {PIPELINE_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "domain": "tepo",
                        "command": "tepo_pipeline_run",
                        "input": {"name": pipeline, "input": input_payload},
                    },
                )
                results["steps"].append(
                    {"step": "pipeline_run", "status": "success", "data": res.json()}
                )
            except Exception as e:
                results["steps"].append(
                    {"step": "pipeline_run", "status": "failed", "error": str(e)}
                )

        # 2️⃣ Tool command (e.g. Render, Git)
        if domain and command:
            try:
                res = await client.post(
                    f"{KITENGA_URL}/mcp/tools/call",
                    headers={
                        "Authorization": f"Bearer {PIPELINE_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={"domain": domain, "command": command, "input": input_payload},
                )
                results["steps"].append(
                    {"step": "tool_call", "status": "success", "data": res.json()}
                )
            except Exception as e:
                results["steps"].append(
                    {"step": "tool_call", "status": "failed", "error": str(e)}
                )

        # 3️⃣ Memory persistence
        if memory:
            summary = f"{intent} | {domain or pipeline} | {input_payload}"
            try:
                await client.post(
                    f"{KITENGA_URL}/awa/memory/add",
                    headers={"Content-Type": "application/json"},
                    json={
                        "content": summary,
                        "metadata": {"trace_id": trace_id, "intent": intent},
                    },
                )
            except Exception as e:
                results["steps"].append(
                    {"step": "memory_add", "status": "failed", "error": str(e)}
                )

        # 4️⃣ Emit protocol event
        try:
            await client.post(
                f"{KITENGA_URL}/awa/protocol/event",
                headers={"Content-Type": "application/json"},
                json={
                    "type": "awa_orchestration_complete",
                    "trace_id": trace_id,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "payload": results,
                },
            )
        except Exception as e:
            results["steps"].append(
                {"step": "event_emit", "status": "failed", "error": str(e)}
            )

    return results


@router.post("/gpt/bridge")
async def gpt_bridge(request: Request):
    """GPT front-door for orchestration requests."""
    body = await request.json()
    query = body.get("query")
    intent = body.get("intent", "auto")
    print(f"🧠 GPT Bridge received query: {query}")

    # Forward to orchestrate endpoint
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{KITENGA_URL}/awa/orchestrate",
            headers={"Content-Type": "application/json"},
            json={
                "intent": intent,
                "pipeline": "summarise",
                "input": {"text": query},
            },
        )
    return resp.json()
