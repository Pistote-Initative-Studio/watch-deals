"""Wrapper for interacting with the eBay Finding API."""

from typing import Any, Dict, List, Optional

import requests

from config import EBAY_APP_ID, get_access_token

# Base endpoint for the eBay Finding API
EBAY_FINDING_URL = "https://svcs.ebay.com/services/search/FindingService/v1"


def _build_filter_entry(fil: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Validate and normalise a single item filter entry.

    Parameters
    ----------
    fil : Dict[str, str]
        Raw filter dictionary supplied by the GUI or caller.

    Returns
    -------
    Optional[Dict[str, str]]
        Cleaned filter entry or ``None`` if the filter should be skipped.
    """

    name = fil.get("name")
    value = fil.get("value")

    # Skip unset or "Any" selections
    if not name or value in (None, "", "Any"):
        return None

    entry: Dict[str, str] = {"name": name, "value": str(value)}

    # Ensure currency is always provided for price filters
    if name in {"MinPrice", "MaxPrice"}:
        entry.setdefault("paramName", "Currency")
        entry.setdefault("paramValue", "USD")

    if fil.get("paramName") and fil.get("paramValue"):
        entry["paramName"] = fil["paramName"]
        entry["paramValue"] = fil["paramValue"]

    return entry


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
        Item filter dictionaries from the GUI. Each filter is flattened into
        ``itemFilter(n)`` groups as required by the eBay Finding API.
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

    filters: List[Dict[str, str]] = []

    for fil in item_filters or []:
        cleaned = _build_filter_entry(fil)
        if cleaned:
            filters.append(cleaned)

    if listing_type:
        filters.append({"name": "ListingType", "value": listing_type})

    # Flatten into indexed itemFilter(n) query parameters
    for idx, fil in enumerate(filters):
        for key, value in fil.items():
            query_params[f"itemFilter({idx}).{key}"] = value
    # ``requests`` will percent-encode parentheses in the ``itemFilter`` keys
    # which the eBay Finding API does not accept.  Build a prepared request
    # and then replace the encoded characters so the original parentheses are
    # preserved without manually assembling the query string.
    session = requests.Session()
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    req = requests.Request("GET", EBAY_FINDING_URL, params=query_params, headers=headers)
    prepared = session.prepare_request(req)
    prepared.url = prepared.url.replace("%28", "(").replace("%29", ")")

    response = session.send(prepared, timeout=10)
    response.raise_for_status()
    return response.json()

