"""Wrapper for interacting with the eBay Finding API."""

from typing import Any, Dict, List, Optional

import requests

from config import EBAY_APP_ID

FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"


def fetch_listings(
    params: Dict[str, Any],
    item_filters: Optional[List[Dict[str, str]]] = None,
    listing_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch listings from eBay using the Finding API.

    Parameters
    ----------
    params : Dict[str, Any]
        Query parameters to send with the request.
    item_filters : Optional[List[Dict[str, str]]]
        List of item filter dictionaries (``name``/``value`` pairs and optional
        ``paramName``/``paramValue``) to be inserted into the request.
    listing_type : Optional[str]
        eBay listing type to include as an ``itemFilter`` entry.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the API.
    """

    if item_filters is None:
        item_filters = []
    else:
        # Copy to avoid mutating the caller's list when appending filters.
        item_filters = list(item_filters)

    if listing_type:
        item_filters.append({"name": "ListingType", "value": listing_type})

    for idx, fil in enumerate(item_filters):
        params[f"itemFilter({idx}).name"] = fil["name"]
        params[f"itemFilter({idx}).value"] = fil["value"]
        if "paramName" in fil:
            params[f"itemFilter({idx}).paramName"] = fil["paramName"]
        if "paramValue" in fil:
            params[f"itemFilter({idx}).paramValue"] = fil["paramValue"]

    headers = {
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-OPERATION-NAME": "findItemsByKeywords",
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON",
    }

    response = requests.get(
        FINDING_API_ENDPOINT, headers=headers, params=params, timeout=10
    )
    response.raise_for_status()
    return response.json()

