from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException
from typing import Any, Dict

from te_po.utils.supabase_client import get_client

router = APIRouter(prefix="/sell", tags=["Cards", "TradeMe"])


@router.post("/add_to_csv")
async def add_to_csv(data: Dict[str, Any] = Body(...)):
    """
    Log a card for Trade Me CSV output by inserting into cards_for_sale.
    """
    supabase = get_client()
    if supabase is None:
        raise HTTPException(status_code=503, detail="Supabase client not configured")
    try:
        supabase.table("cards_for_sale").insert(data).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Insert failed: {exc}")
    return {"status": "added"}
