# src/ebay_api.py
"""
eBay Browse API integration for fetching active listings.
"""

import requests
from typing import List, Dict, Any
from .config import EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, get_access_token

# eBay Browse API endpoint
BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def fetch_listings(
    keyword: str,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    condition: str | None = None,
    listing_type: str | None = None,
    max_time_left: str | None = None,
    exclude_keywords: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Fetch listings from eBay Browse API using keyword search.
    """

    access_token = get_access_token()

    params: Dict[str, Any] = {"q": keyword, "limit": limit}

    # Optional filters
    filter_parts = []
    if min_price is not None:
        filter_parts.append(f"price:[{min_price}..]")
    if max_price is not None:
        filter_parts.append(f"price:[..{max_price}]")
    if condition:
        filter_parts.append(f"conditionIds:{{{condition}}}")
    if listing_type:
        filter_parts.append(f"buyingOptions:{{{listing_type}}}")

    if filter_parts:
        params["filter"] = ",".join(filter_parts)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(BROWSE_SEARCH_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("itemSummaries", [])


if __name__ == "__main__":
    # Simple test run
    items = fetch_listings("seiko", limit=5)
    for item in items:
        title = item.get("title", "Untitled")
        price = item.get("price", {}).get("value", "N/A")
        currency = item.get("price", {}).get("currency", "")
        print(f"{title} - {price} {currency}")
