import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd

from ebay_api import fetch_listings
from excel_exporter import export_to_excel

# Mapping of display labels to official eBay codes/values
CONDITION_OPTIONS = {
    "Any": None,
    "New (1000)": "1000",
    "New other (see details) (1500)": "1500",
    "Manufacturer refurbished (2000)": "2000",
    "Seller refurbished (2500)": "2500",
    "Used (3000)": "3000",
    "For parts or not working (7000)": "7000",
}

LISTING_TYPE_OPTIONS = {
    "Any": None,
    "Auction": "Auction",
    "FixedPrice": "FixedPrice",
    "AuctionWithBIN": "AuctionWithBIN",
}

MAX_TIME_LEFT_OPTIONS = {
    "Any": None,
    "1 hour": "PT1H",
    "1 day": "P1D",
    "5 days": "P5D",
    "10 days": "P10D",
}


def get_condition_code(selection: str | None) -> str | None:
    return CONDITION_OPTIONS.get(selection or "")


def get_listing_type(selection: str | None) -> str | None:
    return LISTING_TYPE_OPTIONS.get(selection or "")


def get_max_time_left(selection: str | None) -> str | None:
    return MAX_TIME_LEFT_OPTIONS.get(selection or "")


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

    item_filters = []
    if max_price:
        try:
            item_filters.append(
                {
                    "name": "MaxPrice",
                    "value": str(float(max_price)),
                    "paramName": "Currency",
                    "paramValue": "USD",
                }
            )
        except ValueError:
            messagebox.showerror("Error", "Invalid max price")
            return
    if min_price:
        try:
            item_filters.append(
                {
                    "name": "MinPrice",
                    "value": str(float(min_price)),
                    "paramName": "Currency",
                    "paramValue": "USD",
                }
            )
        except ValueError:
            messagebox.showerror("Error", "Invalid min price")
            return
    condition_code = get_condition_code(condition_var.get())
    if condition_code:
        item_filters.append({"name": "Condition", "value": condition_code})
    listing_value = get_listing_type(listing_type_var.get())
    if listing_value:
        item_filters.append({"name": "ListingType", "value": listing_value})
    max_time_left_value = get_max_time_left(time_left_var.get())
    if max_time_left_value:
        item_filters.append({"name": "MaxTimeLeft", "value": max_time_left_value})

    try:
        data = fetch_listings(params, item_filters)
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
condition_var = tk.StringVar(value="Any")
condition_menu = ttk.Combobox(root, textvariable=condition_var, state="readonly")
condition_menu["values"] = list(CONDITION_OPTIONS.keys())
condition_menu.current(0)
condition_menu.grid(row=4, column=1, sticky="ew")

# Listing type
tk.Label(root, text="Listing Type").grid(row=5, column=0, sticky="w")
listing_type_var = tk.StringVar(value="Any")
listing_type_menu = ttk.Combobox(root, textvariable=listing_type_var, state="readonly")
listing_type_menu["values"] = list(LISTING_TYPE_OPTIONS.keys())
listing_type_menu.current(0)
listing_type_menu.grid(row=5, column=1, sticky="ew")

# Time left
tk.Label(root, text="Max Time Left").grid(row=6, column=0, sticky="w")
time_left_var = tk.StringVar(value="Any")
time_left_menu = ttk.Combobox(root, textvariable=time_left_var, state="readonly")
time_left_menu["values"] = list(MAX_TIME_LEFT_OPTIONS.keys())
time_left_menu.current(0)
time_left_menu.grid(row=6, column=1, sticky="ew")

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
