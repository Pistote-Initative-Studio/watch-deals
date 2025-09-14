"""Interface to the eBay Finding API."""

import requests
from typing import List, Dict

from config import EBAY_APP_ID

FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"


def fetch_listings(brand: str, max_price: float, entries: int = 20) -> List[Dict]:
    """Fetch watch listings from eBay filtered by brand and maximum price.

    Parameters
    ----------
    brand : str
        Brand keyword to search for. Only a single brand is supported.
    max_price : float
        Maximum listing price in USD.
    entries : int, optional
        Number of results to fetch, by default 20.

    Returns
    -------
    List[Dict]
        A list of dictionaries containing title, price, url, and end_time keys.
    """
    if not EBAY_APP_ID:
        raise ValueError("EBAY_APP_ID environment variable is not set")

    params = {
        "OPERATION-NAME": "findItemsAdvanced",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": f"{brand} watch",
        "paginationInput.entriesPerPage": entries,
        "itemFilter(0).name": "MaxPrice",
        "itemFilter(0).value": max_price,
        "itemFilter(0).paramName": "Currency",
        "itemFilter(0).paramValue": "USD",
        "aspectFilter(0).aspectName": "Brand",
        "aspectFilter(0).aspectValueName": brand,
    }

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
