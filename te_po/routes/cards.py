from __future__ import annotations

import csv as csv_module
import io
import os
import re
import time
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter, Body, File, HTTPException, UploadFile

from te_po.pipeline.cards.card_upload_pipeline import (
    CardListing,
    CardUploadPipeline,
    load_reference_prices,
    estimate_price,
    TRADEME_COLUMNS,
)
from te_po.core.config import settings
from te_po.database.supabase import get_client
from te_po.stealth_ocr import StealthOCR
import logging

router = APIRouter(prefix="/cards", tags=["Cards"])

REF_PATH = "storage/card_reference.csv"
ref_prices = load_reference_prices(REF_PATH)
logger = logging.getLogger("te_po.cards")

VALUE_CACHE_TTL = timedelta(hours=24)
_value_cache: Dict[str, Dict[str, Any]] = {}


def _detect_card_number(text: str) -> Optional[str]:
    patterns = [
        r"[A-Z]{1,3}\d{1,3}[-–]\d{2,3}",
        r"[A-Z]{1,3}\d{1,4}",
        r"\d{3}-\d{3}",
    ]
    text_upper = text.upper()
    for pattern in patterns:
        match = re.search(pattern, text_upper)
        if match:
            return match.group(0).replace("–", "-")
    return None


def _detect_rarity(text: str) -> Optional[str]:
    rarities = [
        "SCR",
        "SPR",
        "SR",
        "UR",
        "SSR",
        "R",
        "UC",
        "C",
        "UNCOMMON",
        "COMMON",
        "RARE",
        "LEGENDARY",
    ]
    text_upper = text.upper()
    for rarity in rarities:
        if re.search(rf"\b{rarity}\b", text_upper):
            return rarity
    return None


def _extract_card_name(text: str, card_number: Optional[str]) -> Optional[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    normalized_number = None
    if card_number:
        normalized_number = card_number.upper().replace("-", "").replace("–", "")
    scored_candidate: Optional[str] = None
    best_score = 0
    number_line_index: Optional[int] = None
    for idx, line in enumerate(lines):
        comparison = re.sub(r"[^A-Z0-9]", "", line.upper())
        if normalized_number and normalized_number in comparison:
            number_line_index = idx
            continue
        if re.search(r"^\d+$", line):
            continue
        letters = sum(1 for ch in line if ch.isalpha())
        digits = sum(1 for ch in line if ch.isdigit())
        if letters < 3:
            continue
        score = letters * 2 - digits * 3 + min(len(line), 80)
        if score > best_score:
            best_score = score
            scored_candidate = line[:160]
    if scored_candidate:
        return scored_candidate
    if number_line_index is not None and number_line_index > 0:
        return lines[number_line_index - 1][:160]
    return lines[0][:160]


@router.post("/scan-image")
async def scan_image(image: UploadFile = File(...)):
    """Run OCR on a card photo to extract card details (name, number, rarity)."""
    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="Image file is required.")
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    scanner = StealthOCR()
    scanner.cultural_encoding_active = False
    result = scanner.real_scan(data)
    raw_text = result.get("raw_text") or result.get("text_extracted") or ""
    cleaned_text = raw_text.replace("\x0c", " ").strip()
    if cleaned_text.lower().startswith("[vision error") or cleaned_text.lower().startswith("[tesseract error"):
        cleaned_text = ""
        raw_text = ""

    card_number = _detect_card_number(cleaned_text)
    rarity = _detect_rarity(cleaned_text)
    card_name = _extract_card_name(cleaned_text, card_number)

    logger.info(
        "scan-image result",
        extra={
            "card_name": card_name,
            "card_number": card_number,
            "rarity": rarity,
            "confidence": result.get("confidence"),
        },
    )

    return {
        "card_name": card_name,
        "card_number": card_number,
        "rarity": rarity,
        "text": cleaned_text,
        "raw_text": raw_text,
        "confidence": result.get("confidence"),
        "method_used": result.get("method_used"),
    }


def _cache_key(card_name: str, card_number: Optional[str]) -> str:
    return f"{card_name.lower()}::{(card_number or '').lower()}"


def _get_cached_value(key: str) -> Optional[Dict[str, Any]]:
    entry = _value_cache.get(key)
    if not entry:
        return None
    if entry["expires"] < datetime.utcnow():
        _value_cache.pop(key, None)
        return None
    return entry["data"]


def _set_cached_value(key: str, data: Dict[str, Any]) -> None:
    _value_cache[key] = {"data": data, "expires": datetime.utcnow() + VALUE_CACHE_TTL}


def _extract_price_from_text(text: str) -> Optional[float]:
    match = re.search(r"\$([0-9]+(?:\.[0-9]{1,2})?)", text.replace(",", ""))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _estimate_value_brave(card_name: str, card_number: Optional[str]) -> Optional[Dict[str, Any]]:
    token = os.getenv("BRAVE_API_WEB_SEARCH") or os.getenv("BRAVE_API_KEY")
    if not token:
        return None
    query_parts = [card_name]
    if card_number:
        query_parts.append(card_number)
    query_parts.append("price")
    query = " ".join([part for part in query_parts if part])
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": token},
            params={"q": query, "count": 5},
            timeout=6,
        )
        if not resp.ok:
            return None
        data = resp.json() or {}
        items = data.get("web", {}).get("results", [])
        for item in items:
            text = " ".join(filter(None, [item.get("title"), item.get("description")]))
            price = _extract_price_from_text(text)
            if price:
                return {
                    "source": "brave",
                    "value": round(price, 2),
                    "url": item.get("url"),
                    "description": text[:240],
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
    except Exception as exc:
        logger.debug("Brave price estimate failed: %s", exc)
    return None


def _fetch_ebay_prices(query: str, operation: str, params: Dict[str, Any]) -> List[float]:
    app_id = os.getenv("EBAY_SEARCH_APP_ID") or os.getenv("EBAY_API_KEY")
    if not app_id:
        return []
    base_params = {
        "OPERATION-NAME": operation,
        "SERVICE-VERSION": "1.13.0",
        "SECURITY-APPNAME": app_id,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": query,
        "paginationInput.entriesPerPage": "30",
    }
    base_params.update(params)
    try:
        resp = requests.get(
            "https://svcs.ebay.com/services/search/FindingService/v1",
            params=base_params,
            timeout=8,
        )
        if not resp.ok:
            return []
        data = resp.json() or {}
        search_result = data.get("findCompletedItemsResponse", data.get("findItemsAdvancedResponse", []))
        if not search_result:
            return []
        items = search_result[0].get("searchResult", [{}])[0].get("item", [])
        prices: List[float] = []
        for item in items:
            selling = item.get("sellingStatus", [{}])[0]
            price_data = selling.get("currentPrice") or selling.get("convertedCurrentPrice") or [{}]
            price_str = price_data[0].get("__value__", "")
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                continue
            if price > 0:
                prices.append(price)
        return prices
    except Exception as exc:
        logger.debug("eBay price fetch failed: %s", exc)
        return []


def _estimate_value_ebay(card_name: str, card_number: Optional[str]) -> List[Dict[str, Any]]:
    query = " ".join(filter(None, [card_name, card_number]))
    if not query:
        return []
    sources: List[Dict[str, Any]] = []

    sold_prices = _fetch_ebay_prices(
        query,
        "findCompletedItems",
        {
            "itemFilter(0).name": "SoldItemsOnly",
            "itemFilter(0).value": "true",
            "itemFilter(1).name": "EndTimeFrom",
            "itemFilter(1).value": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    if sold_prices:
        sources.append(
            {
                "source": "ebay_sold",
                "value": round(sum(sold_prices) / len(sold_prices), 2),
                "url": "https://www.ebay.com/sch/i.html?_nkw=" + requests.utils.quote(query),
                "description": f"Average of {len(sold_prices)} sold listings (7 days)",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )

    active_prices = _fetch_ebay_prices(
        query,
        "findItemsAdvanced",
        {"itemFilter(0).name": "ListingType", "itemFilter(0).value": "FixedPrice"},
    )
    if active_prices:
        sources.append(
            {
                "source": "ebay_active",
                "value": round(sum(active_prices) / len(active_prices), 2),
                "url": "https://www.ebay.com/sch/i.html?_nkw=" + requests.utils.quote(query),
                "description": f"Average of {len(active_prices)} active listings",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )

    return sources


def _estimate_value_pricecheck(card_name: str, card_number: Optional[str]) -> Optional[Dict[str, Any]]:
    api_url = os.getenv("PRICECHECK_API_URL")
    api_key = os.getenv("PRICECHECK_API_KEY")
    if not api_url or not api_key:
        return None
    try:
        resp = requests.get(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            params={"name": card_name, "number": card_number},
            timeout=6,
        )
        if not resp.ok:
            return None
        data = resp.json() or {}
        value = data.get("average_price") or data.get("price")
        if not value:
            return None
        return {
            "source": "pricecheck",
            "value": round(float(value), 2),
            "url": data.get("url"),
            "description": data.get("notes") or "PriceCheck API",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as exc:
        logger.debug("PriceCheck estimate failed: %s", exc)
        return None


@router.post("/estimate-value")
def estimate_value(payload: Dict[str, Any] = Body(...)):
    """Aggregate multi-source valuation for a trading card."""
    card_name = (payload.get("card_name") or payload.get("name") or "").strip()
    card_number = (payload.get("card_number") or payload.get("number") or "").strip() or None
    if not card_name:
        raise HTTPException(status_code=400, detail="card_name is required")

    cache_key = _cache_key(card_name, card_number)
    cached = _get_cached_value(cache_key)
    if cached:
        return {**cached, "cached": True}

    sources: List[Dict[str, Any]] = []

    brave_source = _estimate_value_brave(card_name, card_number)
    if brave_source:
        sources.append(brave_source)

    ebay_sources = _estimate_value_ebay(card_name, card_number)
    if ebay_sources:
        sources.extend(ebay_sources)

    pricecheck_source = _estimate_value_pricecheck(card_name, card_number)
    if pricecheck_source:
        sources.append(pricecheck_source)

    if sources:
        average_price = round(sum(src["value"] for src in sources) / len(sources), 2)
        confidence = min(1.0, 0.35 + 0.15 * (len(sources) - 1))
    else:
        average_price = 0.0
        confidence = 0.0

    result = {
        "card_name": card_name,
        "card_number": card_number,
        "sources": sources,
        "average_price": average_price,
        "confidence": round(confidence, 2),
        "cached": False,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    _set_cached_value(cache_key, result)
    return result


@router.post("/build-row")
def build_row(payload: Dict[str, Any]):
    """Build a Trade Me-ready row from card metadata."""
    card = CardListing(
        name=payload.get("name") or payload.get("title") or "",
        set_name=payload.get("set_name"),
        number=payload.get("number"),
        rarity=payload.get("rarity"),
        price=payload.get("price"),
        buy_now=payload.get("buy_now"),
        description=payload.get("description") or payload.get("description_extra"),
        front_image=payload.get("front_image") or payload.get("photo1"),
        back_image=payload.get("back_image") or payload.get("photo2"),
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
    rows_payload: List[Dict[str, Any]] | None = payload.get("rows")
    columns = payload.get("columns") or TRADEME_COLUMNS
    if rows_payload:
        rows = rows_payload
    else:
        cards_data: List[Dict[str, Any]] = payload.get("cards") or []
        batch = payload.get("groups_of", 10)
        pipeline = CardUploadPipeline()
        rows = []
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
        batches = [rows[i : i + batch] for i in range(0, len(rows), batch)]
    if not rows:
        csv_text = ""
    else:
        buffer = io.StringIO()
        writer = csv_module.DictWriter(buffer, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})
        csv_text = buffer.getvalue()
    response: Dict[str, Any] = {"columns": columns, "rows": rows, "csv": csv_text}
    if not rows_payload:
        response["batches"] = batches
    return response


@router.post("/value")
def card_value(payload: Dict[str, Any]):
    """Lookup card value from reference; fallback to default."""
    name = payload.get("name") or ""
    price = estimate_price(name, ref_prices, 0.10)
    return {"name": name, "price": price}


@router.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    """Upload a single card image to Supabase storage and return its public URL."""
    if image is None:
        raise HTTPException(status_code=400, detail="Image file is required.")
    if not image.filename:
        raise HTTPException(status_code=400, detail="Filename missing for upload.")
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    supabase = get_client()
    if supabase is None:
        raise HTTPException(status_code=503, detail="Supabase client not configured.")

    allowed_ext = {".jpg", ".jpeg", ".png", ".webp"}
    extension = os.path.splitext(image.filename)[1].lower()
    if extension not in allowed_ext:
        extension = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }.get(content_type, ".jpg")

    file_id = uuid4().hex
    dest_path = f"cards/{file_id}{extension}"
    bucket = settings.supabase_bucket_storage or "tepo_storage"

    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        supabase.storage.from_(bucket).upload(dest_path, data, {"content-type": content_type, "upsert": True})
    except Exception as exc:  # pragma: no cover - external service
        raise HTTPException(status_code=502, detail=f"Failed to upload image: {exc}") from exc

    public_url_payload = supabase.storage.from_(bucket).get_public_url(dest_path)
    if isinstance(public_url_payload, dict):
        image_url = (
            public_url_payload.get("publicURL")
            or public_url_payload.get("publicUrl")
            or public_url_payload.get("signedURL")
        )
    else:
        image_url = public_url_payload

    if not image_url:
        raise HTTPException(status_code=502, detail="Failed to retrieve public URL for uploaded image.")

    return {"image_url": image_url, "path": dest_path}
