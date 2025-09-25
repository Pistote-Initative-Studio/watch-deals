"""Command-line entry point for fetching eBay watch listings and exporting them."""

from __future__ import annotations

import sys
from typing import List

import pandas as pd

from .config import DEFAULT_RESULT_LIMIT, DEFAULT_SEARCH_KEYWORD
from .ebay_api import fetch_listings
from .excel_exporter import export_to_excel
from .token_manager import set_token


def _prompt_for_token() -> None:
    """Request an OAuth token from the user before making any API calls."""
    while True:
        try:
            token = input("Paste your eBay token: ").strip()
        except EOFError:  # pragma: no cover - interactive guard
            print("\nNo token provided. Exiting.")
            sys.exit(1)

        if not token:
            print("A token is required to continue. Please paste a valid token.")
            continue

        try:
            set_token(token)
        except ValueError as exc:
            print(exc)
            continue
        break


def main() -> None:
    _prompt_for_token()

    keyword = input(
        f"Enter a search keyword (default '{DEFAULT_SEARCH_KEYWORD}'): "
    ).strip() or DEFAULT_SEARCH_KEYWORD

    limit_input = input(
        f"Number of results to fetch (default {DEFAULT_RESULT_LIMIT}): "
    ).strip()
    try:
        limit = int(limit_input) if limit_input else DEFAULT_RESULT_LIMIT
    except ValueError:
        print("Invalid number provided. Using default limit.")
        limit = DEFAULT_RESULT_LIMIT

    try:
        listings: List[dict] = fetch_listings(keyword=keyword, limit=limit)
    except PermissionError:
        # fetch_listings already prints the token expiry message for 401s
        return
    except Exception as exc:  # pragma: no cover - network failure path
        print(f"Error fetching listings: {exc}")
        return

    if not listings:
        print("No listings found for the provided search term.")
        return

    df = pd.DataFrame(listings)
    export_to_excel(df)
    print(f"✅ Exported {len(df)} listings to listings.xlsx")


if __name__ == "__main__":
    main()
