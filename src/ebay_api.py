"""Interface to the eBay Finding API."""

import requests
from typing import Dict, List, Optional

from config import EBAY_APP_ID

FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"


def fetch_listings(
    brand: str,
    max_price: Optional[float] = None,
    entries: int = 20,
    model_keywords: Optional[str] = None,
    min_price: Optional[float] = None,
    condition: Optional[str] = None,
    listing_type: Optional[str] = None,
    max_time_left: Optional[int] = None,
    exclude_keywords: Optional[str] = None,
) -> List[Dict]:
    """Fetch watch listings from eBay filtered by various parameters.

    Parameters
    ----------
    brand : str
        Brand keyword to search for. Only a single brand is supported.
    max_price : float, optional
        Maximum listing price in USD.
    entries : int, optional
        Number of results to fetch, by default 20.
    model_keywords : str, optional
        Additional model keywords.
    min_price : float, optional
        Minimum listing price in USD.
    condition : {"New", "Used"}, optional
        Filter by condition.
    listing_type : {"Auction", "BIN"}, optional
        Filter by listing type (BIN stands for Buy It Now).
    max_time_left : int, optional
        Maximum time left in hours.
    exclude_keywords : str, optional
        Comma-separated keywords to exclude from search.

    Returns
    -------
    List[Dict]
        A list of dictionaries containing title, price, url, and end_time keys.
    """
    if not EBAY_APP_ID:
        raise ValueError("EBAY_APP_ID environment variable is not set")

    keywords = f"{brand}"
    if model_keywords:
        keywords += f" {model_keywords}"
    keywords += " watch"

    if exclude_keywords:
        for word in exclude_keywords.split(","):
            w = word.strip()
            if w:
                keywords += f" -{w}"

    params = {
        "OPERATION-NAME": "findItemsAdvanced",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": keywords,
        "paginationInput.entriesPerPage": entries,
        "aspectFilter(0).aspectName": "Brand",
        "aspectFilter(0).aspectValueName": brand,
    }

    item_filters: List[Dict[str, str]] = []
    if max_price is not None:
        item_filters.append(
            {
                "name": "MaxPrice",
                "value": str(max_price),
                "paramName": "Currency",
                "paramValue": "USD",
            }
        )
    if min_price is not None:
        item_filters.append(
            {
                "name": "MinPrice",
                "value": str(min_price),
                "paramName": "Currency",
                "paramValue": "USD",
            }
        )
    if condition in {"New", "Used"}:
        condition_code = {"New": "1000", "Used": "3000"}[condition]
        item_filters.append({"name": "Condition", "value": condition_code})
    if listing_type in {"Auction", "BIN"}:
        lt_value = "Auction" if listing_type == "Auction" else "FixedPrice"
        item_filters.append({"name": "ListingType", "value": lt_value})
    if max_time_left:
        item_filters.append(
            {"name": "MaxTimeLeft", "value": f"PT{int(max_time_left)}H"}
        )

    for idx, fil in enumerate(item_filters):
        params[f"itemFilter({idx}).name"] = fil["name"]
        params[f"itemFilter({idx}).value"] = fil["value"]
        if "paramName" in fil:
            params[f"itemFilter({idx}).paramName"] = fil["paramName"]
        if "paramValue" in fil:
            params[f"itemFilter({idx}).paramValue"] = fil["paramValue"]

    response = requests.get(FINDING_API_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    items = (
        data.get("findItemsAdvancedResponse", [{}])[0]
        .get("searchResult", [{}])[0]
        .get("item", [])
    )

    listings: List[Dict] = []
    for item in items:
        title = item.get("title", [""])[0]
        price = (
            item.get("sellingStatus", [{}])[0]
            .get("currentPrice", [{}])[0]
            .get("__value__")
        )
        url = item.get("viewItemURL", [""])[0]
        end_time = item.get("listingInfo", [{}])[0].get("endTime", [""])[0]
        listings.append(
            {
                "title": title,
                "price": float(price) if price is not None else None,
                "url": url,
                "end_time": end_time,
            }
        )

    return listings
