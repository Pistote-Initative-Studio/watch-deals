import tkinter as tk
from tkinter import messagebox
import pandas as pd

from ebay_api import fetch_listings
from excel_exporter import export_to_excel


def fetch_from_gui():
    brand = brand_entry.get().strip()
    model = model_entry.get().strip()
    min_price = min_price_entry.get().strip()
    max_price = max_price_entry.get().strip()
    condition = condition_var.get()
    listing_type = listing_type_var.get()
    time_left = time_left_var.get()
    exclude = exclude_entry.get().strip()
    entries = result_var.get()

    kwargs = {"entries": entries}
    if model:
        kwargs["model_keywords"] = model
    if min_price:
        try:
            kwargs["min_price"] = float(min_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid min price")
            return
    if max_price:
        try:
            kwargs["max_price"] = float(max_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid max price")
            return
    if condition != "Any":
        kwargs["condition"] = condition
    if listing_type != "Both":
        kwargs["listing_type"] = listing_type
    if time_left != "Any":
        kwargs["max_time_left"] = int(time_left.replace("h", ""))
    if exclude:
        kwargs["exclude_keywords"] = exclude

    try:
        listings = fetch_listings(brand, **kwargs)
    except Exception as exc:
        messagebox.showerror("Error", str(exc))
        return

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
condition_menu = tk.OptionMenu(root, condition_var, "Any", "New", "Used")
condition_menu.grid(row=4, column=1, sticky="ew")

# Listing type
tk.Label(root, text="Listing Type").grid(row=5, column=0, sticky="w")
listing_type_var = tk.StringVar(value="Both")
listing_type_menu = tk.OptionMenu(root, listing_type_var, "Auction", "BIN", "Both")
listing_type_menu.grid(row=5, column=1, sticky="ew")

# Time left
tk.Label(root, text="Max Time Left").grid(row=6, column=0, sticky="w")
time_left_var = tk.StringVar(value="Any")
time_left_menu = tk.OptionMenu(root, time_left_var, "Any", "24h", "48h")
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
fetch_button = tk.Button(root, text="Fetch Listings", command=fetch_from_gui)
fetch_button.grid(row=9, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root.mainloop()
