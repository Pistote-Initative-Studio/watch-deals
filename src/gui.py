import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd

from .ebay_api import fetch_listings
from .excel_exporter import export_to_excel

# Mapping of display labels to official eBay codes/values
CONDITION_OPTIONS = {
    "New": "1000",
    "Like New": "1500",
    "Used": "3000",
    "For Parts": "7000",
}

LISTING_TYPE_OPTIONS = {
    "Auction": "Auction",
    "Auction with BIN": "AuctionWithBIN",
    "Fixed Price": "FixedPrice",
    "Classified": "Classified",
}

MAX_TIME_LEFT_OPTIONS = {
    "1 Hour": "PT1H",
    "12 Hours": "PT12H",
    "1 Day": "P1D",
    "3 Days": "P3D",
    "5 Days": "P5D",
}


def run_gui():
    root = tk.Tk()
    root.title("Watch Listings Fetcher")

    # Form fields
    tk.Label(root, text="Brand").grid(row=0, column=0, sticky="w")
    brand_entry = tk.Entry(root)
    brand_entry.grid(row=0, column=1)

    tk.Label(root, text="Model").grid(row=1, column=0, sticky="w")
    model_entry = tk.Entry(root)
    model_entry.grid(row=1, column=1)

    tk.Label(root, text="Min Price").grid(row=2, column=0, sticky="w")
    min_price_entry = tk.Entry(root)
    min_price_entry.grid(row=2, column=1)

    tk.Label(root, text="Max Price").grid(row=3, column=0, sticky="w")
    max_price_entry = tk.Entry(root)
    max_price_entry.grid(row=3, column=1)

    tk.Label(root, text="Condition").grid(row=4, column=0, sticky="w")
    condition_cb = ttk.Combobox(root, values=list(CONDITION_OPTIONS.keys()))
    condition_cb.grid(row=4, column=1)

    tk.Label(root, text="Listing Type").grid(row=5, column=0, sticky="w")
    listing_type_cb = ttk.Combobox(root, values=list(LISTING_TYPE_OPTIONS.keys()))
    listing_type_cb.grid(row=5, column=1)

    tk.Label(root, text="Max Time Left").grid(row=6, column=0, sticky="w")
    time_left_cb = ttk.Combobox(root, values=list(MAX_TIME_LEFT_OPTIONS.keys()))
    time_left_cb.grid(row=6, column=1)

    tk.Label(root, text="Exclude Keywords").grid(row=7, column=0, sticky="w")
    exclude_entry = tk.Entry(root)
    exclude_entry.grid(row=7, column=1)

    tk.Label(root, text="Results").grid(row=8, column=0, sticky="w")
    results_entry = tk.Entry(root)
    results_entry.insert(0, "20")
    results_entry.grid(row=8, column=1)

    def on_fetch():
        try:
            brand = brand_entry.get().strip()
            model = model_entry.get().strip()
            keyword = " ".join(filter(None, [brand, model]))

            min_price = float(min_price_entry.get()) if min_price_entry.get() else None
            max_price = float(max_price_entry.get()) if max_price_entry.get() else None
            condition = CONDITION_OPTIONS.get(condition_cb.get())
            listing_type = LISTING_TYPE_OPTIONS.get(listing_type_cb.get())
            max_time_left = MAX_TIME_LEFT_OPTIONS.get(time_left_cb.get())
            exclude_keywords = exclude_entry.get().strip() or None
            result_count = int(results_entry.get())

            results = fetch_listings(
                keyword=keyword,
                limit=result_count,
                min_price=min_price,
                max_price=max_price,
                condition=condition,
                listing_type=listing_type,
                max_time_left=max_time_left,
                exclude_keywords=exclude_keywords,
            )

            if not results:
                messagebox.showinfo("No Results", "No listings found.")
                return

            df = pd.DataFrame(results)
            export_to_excel(df)
            messagebox.showinfo("Success", f"Fetched and exported {len(results)} listings.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Fetch Listings", command=on_fetch).grid(
        row=9, column=0, columnspan=2, pady=10
    )

    root.mainloop()


if __name__ == "__main__":
    run_gui()
