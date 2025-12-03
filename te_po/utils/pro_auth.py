import datetime
import asyncio
from fastapi import Header, HTTPException

from te_po.utils.supabase_client import supabase
from te_po.utils.supabase_adapter import insert_den


async def verify_pro_key(x_api_key: str | None = Header(None)):
    """Validate Pro API key against Supabase table pro_api_keys."""
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key.")
    if supabase is None:
        raise HTTPException(status_code=500, detail="Supabase client not initialized.")

    loop = asyncio.get_event_loop()

    def _fetch():
        return (
            supabase.table("pro_api_keys")
            .select("id, customer_name, api_key, active, created_at, last_used_at")
            .eq("api_key", x_api_key)
            .limit(1)
            .execute()
        )

    result = await loop.run_in_executor(None, _fetch)
    rows = getattr(result, "data", None) or []
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    row = rows[0]
    if row.get("active") is not True:
        raise HTTPException(status_code=403, detail="API key disabled.")

    # Update last_used_at (best-effort)
    await loop.run_in_executor(
        None,
        lambda: insert_den(
            "pro_api_keys",
            {
                "id": row.get("id"),
                "last_used_at": datetime.datetime.utcnow().isoformat(),
            },
            upsert=True,
        ),
    )
    return row
