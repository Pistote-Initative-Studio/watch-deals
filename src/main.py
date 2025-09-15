"""Command-line entry point for fetching eBay watch listings and exporting them."""

import pandas as pd

from ebay_api import fetch_listings
from excel_exporter import export_to_excel


def main() -> None:
    brand = "Seiko"
    max_price = 500

    params = {
        "keywords": f"{brand} watch",
        "paginationInput.entriesPerPage": 20,
    }
    item_filters = [
        {
            "name": "MaxPrice",
            "value": str(max_price),
            "paramName": "Currency",
            "paramValue": "USD",
        }
    ]

    data = fetch_listings(params, item_filters)
    items = (
        data.get("findItemsByKeywordsResponse", [{}])[0]
        .get("searchResult", [{}])[0]
        .get("item", [])
    )
    listings = []
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
                "Title": title,
                "Price": float(price) if price is not None else None,
                "URL": url,
                "End Time": end_time,
            }
        )

    df = pd.DataFrame(listings, columns=["Title", "Price", "URL", "End Time"])
    export_to_excel(df)
    print(f"✅ Exported {len(df)} listings to listings.xlsx")


if __name__ == "__main__":
    main()
