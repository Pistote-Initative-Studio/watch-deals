"""Wrapper for interacting with the eBay Finding API."""

from typing import Any, Dict, List, Optional

import requests

from config import EBAY_APP_ID

FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"


def build_item_filters(
    min_price: Optional[str], max_price: Optional[str], condition: Optional[str]
) -> List[Dict[str, str]]:
    """Construct eBay ``itemFilter`` objects.

    Filters are appended in the order required by the API:
    MinPrice -> MaxPrice -> Currency -> Condition.  Any ``None`` values are
    ignored, but the relative order of the remaining filters is preserved.

    Parameters
    ----------
    min_price, max_price : Optional[str]
        Minimum and maximum prices supplied by the GUI.
    condition : Optional[str]
        Human-readable condition (e.g. ``"New"`` or ``"Used"``).

    Returns
    -------
    List[Dict[str, str]]
        A list of filter dictionaries ready to be inserted into the request
        parameters.
    """

    item_filters: List[Dict[str, str]] = []

    if min_price:
        item_filters.append({"name": "MinPrice", "value": str(min_price)})
    if max_price:
        item_filters.append({"name": "MaxPrice", "value": str(max_price)})

    # Currency must always be provided, regardless of price filters
    item_filters.append({"name": "Currency", "value": "USD"})

    condition_map = {"New": "1000", "Used": "3000"}
    if condition in condition_map:
        item_filters.append({"name": "Condition", "value": condition_map[condition]})

    return item_filters


def fetch_listings(params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch listings from eBay using the Finding API.

    Parameters
    ----------
    params : Dict[str, Any]
        Query parameters to send with the request.  ``min_price``, ``max_price``
        and ``condition`` values may be included and will be converted into the
        appropriate ``itemFilter`` entries.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the API.
    """

    min_price = params.pop("min_price", None)
    max_price = params.pop("max_price", None)
    condition = params.pop("condition", None)

    for idx, fil in enumerate(build_item_filters(min_price, max_price, condition)):
        params[f"itemFilter({idx}).name"] = fil["name"]
        params[f"itemFilter({idx}).value"] = fil["value"]

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

