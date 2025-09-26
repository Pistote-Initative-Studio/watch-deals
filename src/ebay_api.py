from typing import List, Optional

import requests
from src import token_manager


def fetch_listings(query: dict, token: Optional[str] = None):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    if token is None:
        token = token_manager.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = {}

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

    min_price = (query.get("min_price") or "").strip()
    if min_price:
        filters.append(f"price:[{min_price}..]")

    max_price = (query.get("max_price") or "").strip()
    if max_price:
        filters.append(f"price:[..{max_price}]")

    condition = (query.get("condition") or "").strip()
    if condition:
        filters.append(f"conditions:{{{condition}}}")

    auction_only = bool(query.get("auction_only"))
    listing_type = (query.get("listing_type") or "").strip()
    if auction_only:
        filters.append("listingType:{Auction}")
    elif listing_type:
        filters.append(f"listingType:{{{listing_type}}}")

    if filters:
        params["filter"] = ",".join(filters)

    limit = (query.get("limit") or "").strip()
    if limit:
        params["limit"] = limit

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise RuntimeError(f"eBay API error {resp.status_code}: {resp.text}")

    data = resp.json()
    items = []
    for item in data.get("itemSummaries", []):
        title = item.get("title", "No title")
        price = item.get("price", {}).get("value", "N/A")
        currency = item.get("price", {}).get("currency", "")
        items.append(f"{title} - {price} {currency}")

    return items
