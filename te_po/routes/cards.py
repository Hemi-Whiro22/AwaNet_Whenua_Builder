from __future__ import annotations

from fastapi import APIRouter, Body
from typing import Any, Dict, List

from te_po.pipeline.cards.card_upload_pipeline import (
    CardListing,
    CardUploadPipeline,
    load_reference_prices,
    estimate_price,
    TRADEME_COLUMNS,
)

router = APIRouter(prefix="/cards", tags=["Cards"])

REF_PATH = "storage/card_reference.csv"
ref_prices = load_reference_prices(REF_PATH)


@router.post("/build-row")
def build_row(payload: Dict[str, Any]):
    """Build a Trade Me-ready row from card metadata."""
    card = CardListing(
        name=payload.get("name") or "",
        set_name=payload.get("set_name"),
        number=payload.get("number"),
        rarity=payload.get("rarity"),
        price=payload.get("price"),
        buy_now=payload.get("buy_now"),
        description=payload.get("description"),
        front_image=payload.get("front_image"),
        back_image=payload.get("back_image"),
        sku=payload.get("sku"),
        category=payload.get("category"),
    )
    pipeline = CardUploadPipeline()
    # fill price from reference if missing
    if card.price is None and card.name:
        card.price = estimate_price(card.name, ref_prices, pipeline.default_price)
    row = pipeline.build_row(card)
    return {"columns": TRADEME_COLUMNS, "row": row}


@router.post("/build-csv")
def build_csv(payload: Dict[str, Any]):
    """
    Build a CSV from a list of card objects.
    groups_of: batch size (default 10) for splitting files client-side.
    """
    cards_data: List[Dict[str, Any]] = payload.get("cards") or []
    batch = payload.get("groups_of", 10)
    pipeline = CardUploadPipeline()
    rows: List[Dict[str, Any]] = []
    for item in cards_data:
        card = CardListing(
            name=item.get("name") or "",
            set_name=item.get("set_name"),
            number=item.get("number"),
            rarity=item.get("rarity"),
            price=item.get("price"),
            buy_now=item.get("buy_now"),
            description=item.get("description"),
            front_image=item.get("front_image"),
            back_image=item.get("back_image"),
            sku=item.get("sku"),
            category=item.get("category"),
        )
        if card.price is None and card.name:
            card.price = estimate_price(card.name, ref_prices, pipeline.default_price)
        rows.append(pipeline.build_row(card))
    # split into batches if needed
    batches = [rows[i : i + batch] for i in range(0, len(rows), batch)]
    return {"columns": TRADEME_COLUMNS, "rows": rows, "batches": batches}


@router.post("/value")
def card_value(payload: Dict[str, Any]):
    """Lookup card value from reference; fallback to default."""
    name = payload.get("name") or ""
    price = estimate_price(name, ref_prices, 0.10)
    return {"name": name, "price": price}
