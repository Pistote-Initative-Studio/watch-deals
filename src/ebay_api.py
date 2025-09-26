from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

import requests
from src import token_manager


def fetch_listings(
    query: Optional[dict] = None,
    token: Optional[str] = None,
    *,
    keyword: Optional[str] = None,
    limit: Optional[int] = None,
):
    if query is None:
        query = {}
    else:
        # Avoid mutating the caller's dictionary when we inject CLI defaults.
        query = dict(query)

    if keyword and not query.get("search_query"):
        query["search_query"] = keyword

    if limit is not None and not query.get("limit"):
        query["limit"] = str(limit)

    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    if token is None:
        token = token_manager.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = {}

    condition_id_map = {
        "new": "1000",
        "brand new": "1000",
        "new other": "1500",
        "new with defects": "1750",
        "manufacturer refurbished": "2000",
        "seller refurbished": "2010",
        "like new": "2750",
        "pre-owned": "3000",
        "used": "3000",
        "very good": "4000",
        "good": "5000",
        "fair": "6000",
        "for parts": "7000",
        "not working": "7000",
        "parts": "7000",
    }

    def _normalize_price(value: str) -> Optional[str]:
        try:
            normalized = str(Decimal(value))
        except (InvalidOperation, ValueError):
            return None

        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        return normalized

    def _clean_split(values: str) -> List[str]:
        return [value.strip() for value in values.split(",") if value.strip()]

    search_terms: List[str] = []
    search_query = (query.get("search_query") or "").strip()
    if search_query:
        search_terms.append(search_query)

    brand = (query.get("brand") or "").strip()
    if brand:
        search_terms.append(brand)

    model = (query.get("model") or "").strip()
    if model:
        search_terms.append(model)

    exclude_keywords = (query.get("exclude_keywords") or "").strip()
    if exclude_keywords:
        excluded_parts = [f'-"{kw}"' for kw in _clean_split(exclude_keywords)]
    else:
        excluded_parts = []

    if search_terms or excluded_parts:
        combined_query = " ".join(search_terms + excluded_parts).strip()
        if combined_query:
            params["q"] = combined_query
            query["computed_query"] = combined_query
    else:
        query["computed_query"] = ""

    filters: List[str] = []

    min_price_raw = (query.get("min_price") or "").strip()
    min_price = _normalize_price(min_price_raw) if min_price_raw else None

    max_price_raw = (query.get("max_price") or "").strip()
    max_price = _normalize_price(max_price_raw) if max_price_raw else None

    if min_price is not None or max_price is not None:
        min_part = min_price or ""
        max_part = max_price or ""
        filters.append(f"price:[{min_part}..{max_part}]")

    condition_input = (query.get("condition") or "").strip().lower()
    condition_id = condition_id_map.get(condition_input) if condition_input else None
    if condition_id:
        filters.append(f"conditionIds:{condition_id}")

    auction_only = bool(query.get("auction_only"))
    listing_type = (query.get("listing_type") or "").strip()
    if auction_only:
        filters.append("buyingOptions:{AUCTION}")
    elif listing_type:
        normalized_listing = listing_type.replace(" ", "_").upper()
        filters.append(f"buyingOptions:{{{normalized_listing}}}")

    if filters:
        params["filter"] = ",".join(filters)

    limit = (query.get("limit") or "").strip()
    if limit:
        params["limit"] = limit

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise RuntimeError(f"eBay API error {resp.status_code}: {resp.text}")

    data = resp.json()
    items: List[Dict[str, str]] = []
    for item in data.get("itemSummaries", []):
        title = item.get("title", "No title")

        price_info = item.get("price") or {}
        price_value = price_info.get("value")
        currency = price_info.get("currency")
        if price_value is not None and currency:
            price = f"{price_value} {currency}"
        elif price_value is not None:
            price = str(price_value)
        else:
            price = "N/A"

        raw_end_date = item.get("itemEndDate")
        time_left = "N/A"
        if raw_end_date:
            try:
                end_dt = datetime.fromisoformat(raw_end_date.replace("Z", "+00:00"))
                delta = end_dt - datetime.now(timezone.utc)
                if delta.total_seconds() <= 0:
                    time_left = "Ended"
                else:
                    days = delta.days
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes = remainder // 60
                    parts = []
                    if days:
                        parts.append(f"{days}d")
                    if hours:
                        parts.append(f"{hours}h")
                    if minutes:
                        parts.append(f"{minutes}m")
                    if not parts:
                        parts.append("<1m")
                    time_left = " ".join(parts)
            except ValueError:
                time_left = raw_end_date

        seller_info = item.get("seller") or {}
        seller_rating = seller_info.get("feedbackPercentage")
        if seller_rating is None:
            seller_rating = seller_info.get("feedbackScore")
        seller_rating_str = str(seller_rating) if seller_rating is not None else "N/A"
        seller_username = seller_info.get("username") or "N/A"

        url = item.get("itemWebUrl", "")

        items.append(
            {
                "title": title,
                "price": price,
                "condition": item.get("condition") or "N/A",
                "time_left": time_left,
                "seller_rating": seller_rating_str,
                "seller": seller_username,
                "url": url,
                "item_id": item.get("itemId") or "",
            }
        )

    return items
