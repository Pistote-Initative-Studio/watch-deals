"""Wrapper for interacting with the eBay Finding API."""

from typing import Any, Dict

import requests

from config import EBAY_APP_ID

FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"


def fetch_listings(params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch listings from eBay using the Finding API.

    Parameters
    ----------
    params : Dict[str, Any]
        Query parameters to send with the request.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON response from the API.
    """

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

