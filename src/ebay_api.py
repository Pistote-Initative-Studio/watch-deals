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
        eBay listing type to include as a top-level request parameter.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the API.
    """

    if item_filters:
        processed_filters: List[Dict[str, str]] = []
        for fil in item_filters:
            # ListingType must be a top-level parameter, not an item filter
            if fil.get("name") == "ListingType":
                listing_type = fil.get("value")
                continue
            processed_filters.append(fil)

        for idx, fil in enumerate(processed_filters):
            params[f"itemFilter({idx}).name"] = fil["name"]
            params[f"itemFilter({idx}).value"] = fil["value"]
            if "paramName" in fil:
                params[f"itemFilter({idx}).paramName"] = fil["paramName"]
            if "paramValue" in fil:
                params[f"itemFilter({idx}).paramValue"] = fil["paramValue"]

    if listing_type:
        params["listingType"] = listing_type

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

