"""Utilities for interacting with the eBay Browse API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .config import EBAY_BROWSE_SEARCH_URL
from .token_manager import get_token


def _build_params(
    keyword: str,
    limit: int,
    *,
    exclude_keywords: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct request parameters for the Browse API search endpoint."""
    params: Dict[str, Any] = {"q": keyword or "watch", "limit": max(1, limit)}

    if exclude_keywords:
        params["q"] = f"{params['q']} -{exclude_keywords}".strip()

    return params


def _normalise_listings(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a simplified representation of eBay Browse API items."""
    normalised: List[Dict[str, Any]] = []
    for item in raw_items:
        price_info = item.get("price") or {}
        item_price = price_info.get("value")
        try:
            price_value = float(item_price) if item_price is not None else None
        except (TypeError, ValueError):
            price_value = None

        normalised.append(
            {
                "Title": item.get("title"),
                "Price": price_value,
                "Currency": price_info.get("currency"),
                "URL": item.get("itemWebUrl"),
                "End Time": item.get("itemEndDate"),
                "Seller": (item.get("seller") or {}).get("username"),
                "Marketplace": item.get("itemLocation"),
            }
        )
    return normalised


def fetch_listings(
    keyword: str = "seiko",
    limit: int = 10,
    *,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    listing_type: Optional[str] = None,
    max_time_left: Optional[str] = None,
    exclude_keywords: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search eBay listings using the Browse API.

    Only keyword and limit are sent directly to the API. The additional keyword-only
    arguments are accepted for GUI compatibility and may be applied locally in the
    future.
    """

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = _build_params(
        keyword=keyword,
        limit=limit,
        exclude_keywords=exclude_keywords,
    )

    try:
        response = requests.get(
            EBAY_BROWSE_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=10,
        )
    except requests.RequestException as exc:  # pragma: no cover - network failure
        raise RuntimeError(f"Failed to contact eBay API: {exc}") from exc

    if response.status_code == 401:
        print("Token expired, please restart app and paste a new token.")
        raise PermissionError("eBay API token expired")

    if not response.ok:
        raise RuntimeError(
            f"❌ API request failed: {response.status_code}, {response.text}"
        )

    data = response.json()
    raw_items = data.get("itemSummaries") or []

    filtered_items = _normalise_listings(raw_items)

    if min_price is not None:
        filtered_items = [
            item
            for item in filtered_items
            if item["Price"] is None or item["Price"] >= float(min_price)
        ]
    if max_price is not None:
        filtered_items = [
            item
            for item in filtered_items
            if item["Price"] is None or item["Price"] <= float(max_price)
        ]

    # Currently the condition, listing_type, and max_time_left parameters are accepted
    # to preserve the public interface used by the GUI. They are not applied because
    # the Browse API requires a more complex filter expression that is beyond the scope
    # of this change.

    return filtered_items
