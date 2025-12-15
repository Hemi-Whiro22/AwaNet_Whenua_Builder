from __future__ import annotations

import csv
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DESCRIPTION = (
    "See other listings. Free shipping over $80. "
    "Free stack of commons/uncommons every $20 spent."
)

# Trade Me bulk import can be finicky about column order. This header is a safe default.
TRADEME_COLUMNS = [
    "Title",
    "Subtitle",
    "Description",
    "StartPrice",
    "ReservePrice",
    "BuyNowPrice",
    "Duration",
    "Pickup",
    "ShippingOption1",
    "ShippingPrice1",
    "ShippingOption2",
    "ShippingPrice2",
    "Photo1",
    "Photo2",
    "SKU",
    "Category",
]


@dataclass
class CardListing:
    name: str
    set_name: Optional[str] = None
    number: Optional[str] = None
    rarity: Optional[str] = None
    price: Optional[float] = None
    buy_now: Optional[float] = None
    description: Optional[str] = None
    front_image: Optional[str] = None  # path or URL
    back_image: Optional[str] = None   # path or URL
    sku: Optional[str] = None
    category: Optional[str] = None


class CardUploadPipeline:
    def __init__(self, default_category: str = "Trading cards", default_price: float = 0.10):
        self.default_category = default_category
        self.default_price = default_price

    def build_title(self, card: CardListing) -> str:
        parts = [card.name]
        if card.set_name:
            parts.append(card.set_name)
        if card.rarity:
            parts.append(card.rarity)
        if card.number:
            parts.append(f"#{card.number}")
        return " - ".join([p for p in parts if p])

    def build_description(self, card: CardListing) -> str:
        desc_parts = [card.description or DEFAULT_DESCRIPTION]
        meta = []
        if card.set_name:
            meta.append(f"Set: {card.set_name}")
        if card.number:
            meta.append(f"Card No: {card.number}")
        if card.rarity:
            meta.append(f"Rarity: {card.rarity}")
        if meta:
            desc_parts.append(" | ".join(meta))
        return "\n".join(desc_parts)

    def build_row(self, card: CardListing) -> Dict[str, Any]:
        title = self.build_title(card)
        desc = self.build_description(card)
        start_price = card.price if card.price is not None else self.default_price
        buy_now = card.buy_now if card.buy_now is not None else None
        row = {
            "Title": title,
            "Subtitle": "",
            "Description": desc,
            "StartPrice": start_price,
            "ReservePrice": "",
            "BuyNowPrice": buy_now or "",
            "Duration": 7,
            "Pickup": "No",
            "ShippingOption1": "Custom: Free shipping over $80",
            "ShippingPrice1": 0,
            "ShippingOption2": "Economy",
            "ShippingPrice2": 5,
            "Photo1": card.front_image or "",
            "Photo2": card.back_image or "",
            "SKU": card.sku or "",
            "Category": card.category or self.default_category,
        }
        return row

    def rows_to_csv(self, rows: List[Dict[str, Any]]) -> str:
        output = []
        writer = csv.DictWriter(output := [], fieldnames=TRADEME_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return "\n".join(output)


def load_reference_prices(path: str) -> Dict[str, float]:
    ref = {}
    p = Path(path)
    if not p.exists():
        return ref
    with p.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("name") or "").strip()
            price = row.get("price") or row.get("value")
            try:
                ref[name] = float(price)
            except Exception:
                continue
    return ref


def estimate_price(name: str, ref: Dict[str, float], fallback: float = 0.10) -> float:
    return ref.get(name.strip(), fallback)
