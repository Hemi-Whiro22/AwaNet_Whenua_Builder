"""
Awa ↔ Kitenga Event Sync Loop
Continuously syncs health, telemetry, and reauth signals between Te Pō and Kitenga MCP.
"""
import asyncio
import httpx
import os
import datetime
import uuid

KITENGA_URL = os.getenv("KITENGA_MCP_URL", "http://127.0.0.1:8000")
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")


async def awa_event_loop():
    """Periodic event sync between Awa and Kitenga."""
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # 1️⃣ Health ping
                r = await client.get(
                    f"{KITENGA_URL}/mcp/health",
                    headers={"Authorization": f"Bearer {PIPELINE_TOKEN}"}
                )
                if r.status_code == 200:
                    print(f"💚 Kitenga alive — {r.json().get('timestamp')}")

                # 2️⃣ Emit Awa heartbeat event
                event = {
                    "type": "awa_heartbeat",
                    "trace_id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "payload": {"status": "alive", "source": "te_po"},
                }
                await client.post(
                    f"{KITENGA_URL}/awa/protocol/event",
                    headers={"Content-Type": "application/json"},
                    json=event,
                )

                # 3️⃣ Optional: re-auth or diagnostics check
                # Future: fetch diagnostics from /debug/routes etc.
        except Exception as e:
            print(f"⚠️ Awa sync loop error: {e}")

        await asyncio.sleep(60)  # every minute


def start_awa_event_loop():
    """Start the Awa sync loop in the background."""
    try:
        asyncio.get_event_loop().create_task(awa_event_loop())
        print("🌊 Awa event sync loop started.")
    except RuntimeError:
        # For async context startup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(awa_event_loop())
        print("🌊 Awa event sync loop started in new loop.")
