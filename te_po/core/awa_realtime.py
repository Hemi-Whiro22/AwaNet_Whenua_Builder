import asyncio
import os
import json
import httpx
import datetime
from fastapi import APIRouter
from typing import Optional
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SUPABASE_WS_URL = os.getenv("SUPABASE_WS_URL")
KITENGA_URL = os.getenv("KITENGA_URL", "https://kitenga-core-js.onrender.com")

realtime_enabled = False
realtime_task = None
last_events = []


async def awa_realtime_listener():
    print("🌊 AwaGPT realtime listener started...")
    global last_events
    async with httpx.AsyncClient() as client_http:
        while realtime_enabled:
            try:
                res = await client_http.get(f"{KITENGA_URL}/awa/sync/debug")
                data = res.json().get("recent_events", [])
                for event in data:
                    if event not in last_events:
                        print(f"🪶 New Awa event: {event['type']}")
                        last_events.append(event)
                        await handle_awa_event(event)
                await asyncio.sleep(10)
            except Exception as e:
                print(f"⚠️ Realtime listener error: {e}")
                await asyncio.sleep(15)


async def handle_awa_event(event):
    event_type = event.get("type")
    payload = event.get("payload", {})
    desc = f"Awa event '{event_type}' received with data: {json.dumps(payload)[:300]}"

    # Use GPT to generate reflection or action
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are AwaGPT, an aware system that reflects and reasons on live Awa events."},
                {"role": "user", "content": desc},
            ]
        )
        reflection = response.choices[0].message.content
        print(f"🧠 Awa Reflection: {reflection}")

        # Optionally store as memory in Kitenga
        async with httpx.AsyncClient() as client_http:
            await client_http.post(
                f"{KITENGA_URL}/awa/memory/add",
                headers={"Content-Type": "application/json"},
                json={
                    "content": reflection,
                    "metadata": {"source": "AwaGPT", "event_type": event_type, "timestamp": datetime.datetime.utcnow().isoformat()},
                },
            )
    except Exception as e:
        print(f"⚠️ GPT reflection failed: {e}")


@router.post("/awa/gpt/realtime/toggle", tags=["AwaGPT Realtime"])
async def toggle_realtime():
    global realtime_enabled, realtime_task
    if realtime_enabled:
        realtime_enabled = False
        return {"status": "stopped"}
    else:
        realtime_enabled = True
        realtime_task = asyncio.create_task(awa_realtime_listener())
        return {"status": "started"}


@router.get("/awa/gpt/realtime/status", tags=["AwaGPT Realtime"])
async def realtime_status():
    return {
        "enabled": realtime_enabled,
        "last_seen": last_events[-3:] if last_events else [],
    }
