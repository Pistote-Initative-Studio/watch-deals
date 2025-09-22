"""Manual test script that queries the eBay Browse API.

This script relies on :func:`config.get_access_token` to obtain an OAuth token
automatically using the client credentials stored in ``.env``.  To run the
script make sure the following variables are present in your environment::

    EBAY_CLIENT_ID="your-client-id"
    EBAY_CLIENT_SECRET="your-client-secret"

Once configured you can execute ``python src/test_raw_request.py watch`` to
print a summary of the first 10 search results including the title, price, and
item URL.
"""

from __future__ import annotations

import sys
from typing import Iterable, List

import requests

from .config import get_access_token

BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
# Sensible defaults to exercise the Browse API in a development environment.
DEFAULT_KEYWORD = "watch"
DEFAULT_RESULT_LIMIT = 20


def search_browse_api(access_token: str, keyword: str, limit: int = DEFAULT_RESULT_LIMIT) -> List[dict]:
    """Query the Browse API for items matching ``keyword``."""

    response = requests.get(
        BROWSE_SEARCH_URL,
        params={"q": keyword, "limit": str(limit)},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    items = payload.get("itemSummaries")
    if not isinstance(items, list):
        return []
    return items


def _format_price(item: dict) -> str:
    """Create a human-readable price string from an item summary."""

    price_info = item.get("price") or {}
    value = price_info.get("value")
    currency = price_info.get("currency")
    if value and currency:
        return f"{value} {currency}"
    if value:
        return str(value)
    return "Price unavailable"


def _iter_display_lines(items: Iterable[dict]) -> Iterable[str]:
    """Yield formatted lines for each item summary."""

    for index, item in enumerate(items, start=1):
        title = item.get("title") or "Untitled item"
        price = _format_price(item)
        url = item.get("itemWebUrl") or item.get("itemAffiliateWebUrl") or "No URL available"
        yield f"{index:02d}. {title} | {price} | {url}"


def main() -> None:
    """Entry point for running the Browse API smoke test."""

    keyword = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KEYWORD

    print("Fetching OAuth token via config.get_access_token()...")
    access_token = get_access_token()

    print(f"Searching Browse API for keyword: {keyword!r}")
    items = search_browse_api(access_token, keyword)
    if not items:
        print("No items returned by the Browse API.")
        return

    print("Results:")
    for line in _iter_display_lines(items[:10]):
        print(line)


if __name__ == "__main__":
    try:
        main()
    except EnvironmentError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        sys.exit(1)
    except requests.HTTPError as exc:
        # Surface HTTP errors directly to aid debugging of authentication or
        # request issues.
        sys.stderr.write(f"HTTP error: {exc.response.status_code} {exc.response.text}\n")
        sys.exit(1)
    except requests.RequestException as exc:
        sys.stderr.write(f"Network error: {exc}\n")
        sys.exit(1)
