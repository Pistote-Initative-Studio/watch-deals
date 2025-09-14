"""Command-line entry point for fetching eBay watch listings and exporting them."""

import pandas as pd

from ebay_api import fetch_listings
from excel_exporter import export_to_excel


def main() -> None:
    brand = "Seiko"
    max_price = 500

    listings = fetch_listings(brand, max_price)
    df = pd.DataFrame(listings)
    if not df.empty:
        df.rename(
            columns={
                "title": "Title",
                "price": "Price",
                "url": "URL",
                "end_time": "End Time",
            },
            inplace=True,
        )
    else:
        df = pd.DataFrame(columns=["Title", "Price", "URL", "End Time"])

    export_to_excel(df)
    print(f"✅ Exported {len(df)} listings to listings.xlsx")


if __name__ == "__main__":
    main()
