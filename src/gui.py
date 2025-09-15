import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd

from ebay_api import fetch_listings
from excel_exporter import export_to_excel

# Mapping of display labels to official eBay codes/values
CONDITION_OPTIONS = {
    "New (1000)": "1000",
    "New other (see details) (1500)": "1500",
    "Manufacturer refurbished (2000)": "2000",
    "Seller refurbished (2500)": "2500",
    "Used (3000)": "3000",
    "For parts or not working (7000)": "7000",
}

LISTING_TYPE_OPTIONS = {
    "Auction": "Auction",
    "FixedPrice": "FixedPrice",
    "AuctionWithBIN": "AuctionWithBIN",
}

MAX_TIME_LEFT_OPTIONS = {
    "1hr": "PT1H",
    "1day": "P1D",
    "5days": "P5D",
    "10days": "P10D",
}


def build_item_filters(
    min_price: float | None = None,
    max_price: float | None = None,
    condition: str | None = None,
    listing_type: str | None = None,
) -> list[dict[str, str]]:
    """Construct item filters for the eBay Finding API.

    Parameters are optional and only provided filters will be included.
    Currency for price filters is always USD.
    """

    filters: list[dict[str, str]] = []

    if condition:
        filters.append({"name": "Condition", "value": condition})

    if listing_type:
        filters.append({"name": "ListingType", "value": listing_type})

    if min_price is not None:
        filters.append(
            {
                "name": "MinPrice",
                "value": str(min_price),
                "paramName": "Currency",
                "paramValue": "USD",
            }
        )

    if max_price is not None:
        filters.append(
            {
                "name": "MaxPrice",
                "value": str(max_price),
                "paramName": "Currency",
                "paramValue": "USD",
            }
        )

    return filters


def get_condition_code(selection: str | None) -> str | None:
    return CONDITION_OPTIONS.get(selection)


def get_listing_type(selection: str | None) -> str | None:
    return LISTING_TYPE_OPTIONS.get(selection)


def get_max_time_left(selection: str | None) -> str | None:
    return MAX_TIME_LEFT_OPTIONS.get(selection)


def on_fetch_click():
    brand = brand_entry.get().strip()
    model = model_entry.get().strip()
    min_price = min_price_entry.get().strip()
    max_price = max_price_entry.get().strip()
    exclude = exclude_entry.get().strip()
    entries = result_var.get()

    if not brand:
        messagebox.showerror("Error", "Brand is required")
        return

    keywords = f"{brand}"
    if model:
        keywords += f" {model}"
    keywords += " watch"
    if exclude:
        for word in exclude.split(","):
            w = word.strip()
            if w:
                keywords += f" -{w}"

    params = {
        "keywords": keywords,
        "paginationInput.entriesPerPage": entries,
    }

    # Validate numeric inputs before building filters
    min_price_val = None
    if min_price:
        try:
            min_price_val = float(min_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid min price")
            return

    max_price_val = None
    if max_price:
        try:
            max_price_val = float(max_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid max price")
            return

    condition_code = get_condition_code(condition_var.get())
    listing_value = get_listing_type(listing_type_var.get())

    filters = build_item_filters(
        min_price=min_price_val,
        max_price=max_price_val,
        condition=condition_code,
        listing_type=listing_value,
    )

    max_time_left_value = get_max_time_left(time_left_var.get())
    if max_time_left_value:
        filters.append({"name": "MaxTimeLeft", "value": max_time_left_value})

    for idx, fil in enumerate(filters):
        params[f"itemFilter({idx}).name"] = fil["name"]
        params[f"itemFilter({idx}).value"] = fil["value"]
        if fil.get("paramName"):
            params[f"itemFilter({idx}).paramName"] = fil["paramName"]
        if fil.get("paramValue"):
            params[f"itemFilter({idx}).paramValue"] = fil["paramValue"]

    try:
        data = fetch_listings(params)
    except Exception as exc:
        messagebox.showerror("Error", str(exc))
        return

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
    messagebox.showinfo("Success", f"Exported {len(df)} listings to listings.xlsx")


root = tk.Tk()
root.title("Watch Listings Fetcher")

# Brand
tk.Label(root, text="Brand").grid(row=0, column=0, sticky="w")
brand_entry = tk.Entry(root)
brand_entry.grid(row=0, column=1)

# Model keywords
tk.Label(root, text="Model").grid(row=1, column=0, sticky="w")
model_entry = tk.Entry(root)
model_entry.grid(row=1, column=1)

# Min price
tk.Label(root, text="Min Price").grid(row=2, column=0, sticky="w")
min_price_entry = tk.Entry(root)
min_price_entry.grid(row=2, column=1)

# Max price
tk.Label(root, text="Max Price").grid(row=3, column=0, sticky="w")
max_price_entry = tk.Entry(root)
max_price_entry.grid(row=3, column=1)

# Condition
tk.Label(root, text="Condition").grid(row=4, column=0, sticky="w")
condition_var = tk.StringVar()
condition_combo = ttk.Combobox(root, textvariable=condition_var, state="readonly")
condition_combo["values"] = list(CONDITION_OPTIONS.keys())
condition_combo.grid(row=4, column=1, sticky="ew")

# Listing type
tk.Label(root, text="Listing Type").grid(row=5, column=0, sticky="w")
listing_type_var = tk.StringVar()
listing_type_combo = ttk.Combobox(root, textvariable=listing_type_var, state="readonly")
listing_type_combo["values"] = list(LISTING_TYPE_OPTIONS.keys())
listing_type_combo.grid(row=5, column=1, sticky="ew")

# Time left
tk.Label(root, text="Max Time Left").grid(row=6, column=0, sticky="w")
time_left_var = tk.StringVar()
time_left_combo = ttk.Combobox(root, textvariable=time_left_var, state="readonly")
time_left_combo["values"] = list(MAX_TIME_LEFT_OPTIONS.keys())
time_left_combo.grid(row=6, column=1, sticky="ew")

# Exclude keywords
tk.Label(root, text="Exclude Keywords").grid(row=7, column=0, sticky="w")
exclude_entry = tk.Entry(root)
exclude_entry.grid(row=7, column=1)

# Result count
tk.Label(root, text="Results").grid(row=8, column=0, sticky="w")
result_var = tk.IntVar(value=20)
result_scale = tk.Scale(root, from_=10, to=100, orient=tk.HORIZONTAL, variable=result_var)
result_scale.grid(row=8, column=1, sticky="ew")

# Fetch button
fetch_button = tk.Button(root, text="Fetch Listings", command=on_fetch_click)
fetch_button.grid(row=9, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root.mainloop()
