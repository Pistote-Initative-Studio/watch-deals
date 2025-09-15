"""Wrapper for interacting with the eBay Finding API."""

from collections import OrderedDict
from typing import Any, Dict, List, Optional

import requests

from config import EBAY_APP_ID

# Base endpoint for the eBay Finding API
EBAY_FINDING_URL = "https://svcs.ebay.com/services/search/FindingService/v1"


def fetch_listings(
    params: Dict[str, Any],
    item_filters: Optional[List[Dict[str, str]]] = None,
    listing_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch listings from eBay using the Finding API.

    Parameters
    ----------
    params : Dict[str, Any]
        Base query parameters such as keywords and pagination limits.
    item_filters : Optional[List[Dict[str, str]]]
        Item filter dictionaries from the GUI. ``paramName``/``paramValue``
        entries (e.g. ``Currency``) are collected and added exactly once.
    listing_type : Optional[str]
        eBay listing type to include as an ``itemFilter`` entry.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the API.
    """

    # Required parameters for all requests
    query_params: Dict[str, Any] = {
        "OPERATION-NAME": "findItemsAdvanced",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
    }
    query_params.update(params)

    filters: "OrderedDict[str, str]" = OrderedDict()
    currency: Optional[str] = None

    for fil in item_filters or []:
        name = fil.get("name")
        value = fil.get("value")
        if not name or value in (None, ""):
            continue
        filters[name] = value
        if fil.get("paramName") == "Currency" and fil.get("paramValue"):
            currency = fil["paramValue"]

    if listing_type:
        filters["ListingType"] = listing_type

    if currency and "Currency" not in filters:
        filters["Currency"] = currency

    for idx, (name, value) in enumerate(filters.items()):
        query_params[f"itemFilter({idx}).name"] = name
        query_params[f"itemFilter({idx}).value"] = value

    response = requests.get(EBAY_FINDING_URL, params=query_params, timeout=10)
    response.raise_for_status()
    return response.json()

