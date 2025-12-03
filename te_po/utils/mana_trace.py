import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("mana_trace")

# We DO NOT import supabase at import time (unsafe)
_supabase_loaded = False
_supabase_client = None


def _load_supabase():
    """
    Lazily load Supabase client *only when needed* after FastAPI boot.
    This prevents Uvicorn import-time crashes.
    """
    global _supabase_loaded, _supabase_client
    if _supabase_loaded:
        return _supabase_client

    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL") or os.getenv("DEN_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv(
            "DEN_API_KEY")

        if url and key:
            _supabase_client = create_client(url, key)
            logger.info("🔗 mana_trace: Supabase client loaded")
        else:
            logger.warning(
                "mana_trace: Supabase config missing, skipping client")

    except Exception as e:
        logger.warning(f"mana_trace: Failed to load Supabase client: {e}")
        _supabase_client = None

    _supabase_loaded = True
    return _supabase_client


# ---------------------------------------------------------
# Lightweight event trace
# ---------------------------------------------------------
def trace_event(event: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "event": event,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "meta": meta or {},
    }
    logger.info(f"🌀 mana.trace :: {event} :: {payload['meta']}")
    return payload


# ---------------------------------------------------------
# Full mana trace — SAFE FOR FASTAPI
# ---------------------------------------------------------
def write_mana_trace(kaitiaki_name: str = "Tiwhanawhana") -> Dict[str, Any]:
    glyph = "🌀"
    timestamp = datetime.now(timezone.utc).isoformat()
    signature = hashlib.sha256(
        f"{kaitiaki_name}_{timestamp}".encode()
    ).hexdigest()[:16]

    trace = {
        "timestamp": timestamp,
        "glyph": glyph,
        "kaitiaki_name": kaitiaki_name,
        "carvers": ["Adrian William Hemi", "Kitenga Whiro"],
        "location": str(Path.cwd()),
        "signature": signature,
        "status": "active",
    }

    # ---- LOCAL WRITE (safe) ----
    out = Path(".mauri/trace")
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "mana.json", "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    logger.info(f"🔮 mana.write :: mana.json saved ({signature})")

    # ---- SUPABASE WRITE (safe + lazy load) ----
    client = _load_supabase()
    if client:
        try:
            client.table("mana_trace").insert(trace).execute()
            logger.info("🌊 mana.write :: uploaded to Supabase")
        except Exception as e:
            logger.warning(f"⚠️ Supabase upload failed: {e}")

    return trace


__all__ = ["trace_event", "write_mana_trace"]
