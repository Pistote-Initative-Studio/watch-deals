import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable
import pandas as pd

from . import token_manager
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


def _build_main_window(root: tk.Tk) -> None:
    """Create the main Watch Listings Fetcher UI once a token is provided."""

    root.deiconify()
    root.title("Watch Listings Fetcher")
    root.geometry("")  # reset any geometry set during the token prompt

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    for column in range(2):
        main_frame.columnconfigure(column, weight=1)

    # Form fields
    ttk.Label(main_frame, text="Brand").grid(row=0, column=0, sticky="w", pady=2)
    brand_entry = ttk.Entry(main_frame)
    brand_entry.grid(row=0, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Model").grid(row=1, column=0, sticky="w", pady=2)
    model_entry = ttk.Entry(main_frame)
    model_entry.grid(row=1, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Min Price").grid(row=2, column=0, sticky="w", pady=2)
    min_price_entry = ttk.Entry(main_frame)
    min_price_entry.grid(row=2, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Max Price").grid(row=3, column=0, sticky="w", pady=2)
    max_price_entry = ttk.Entry(main_frame)
    max_price_entry.grid(row=3, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Condition").grid(row=4, column=0, sticky="w", pady=2)
    condition_cb = ttk.Combobox(main_frame, values=list(CONDITION_OPTIONS.keys()))
    condition_cb.grid(row=4, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Listing Type").grid(row=5, column=0, sticky="w", pady=2)
    listing_type_cb = ttk.Combobox(main_frame, values=list(LISTING_TYPE_OPTIONS.keys()))
    listing_type_cb.grid(row=5, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Max Time Left").grid(row=6, column=0, sticky="w", pady=2)
    time_left_cb = ttk.Combobox(main_frame, values=list(MAX_TIME_LEFT_OPTIONS.keys()))
    time_left_cb.grid(row=6, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Exclude Keywords").grid(row=7, column=0, sticky="w", pady=2)
    exclude_entry = ttk.Entry(main_frame)
    exclude_entry.grid(row=7, column=1, sticky="ew", pady=2)

    ttk.Label(main_frame, text="Results").grid(row=8, column=0, sticky="w", pady=2)
    results_entry = ttk.Entry(main_frame)
    results_entry.insert(0, "20")
    results_entry.grid(row=8, column=1, sticky="ew", pady=2)

    def on_fetch() -> None:
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
                messagebox.showinfo("No Results", "No listings found.", parent=root)
                return

            df = pd.DataFrame(results)
            export_to_excel(df)
            messagebox.showinfo(
                "Success", f"Fetched and exported {len(results)} listings.", parent=root
            )

        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=root)

    fetch_button = ttk.Button(main_frame, text="Fetch Listings", command=on_fetch)
    fetch_button.grid(row=9, column=0, columnspan=2, pady=10)

    brand_entry.focus_set()


def _prompt_for_token(root: tk.Tk, on_success: Callable[[], None]) -> None:
    """Display a modal dialog requesting the user's eBay OAuth token."""

    token_window = tk.Toplevel(root)
    token_window.title("Enter eBay OAuth Token")
    token_window.resizable(False, False)
    token_window.transient(root)
    token_window.grab_set()

    ttk.Label(
        token_window,
        text=(
            "Paste your eBay OAuth token to continue.\n"
            "The token is stored only for this session."
        ),
        justify="left",
        padding=10,
    ).pack(fill="x")

    entry = ttk.Entry(token_window, width=60)
    entry.pack(padx=10, pady=(0, 10))

    def submit_token(event=None):  # type: ignore[unused-argument]
        token_value = entry.get()
        try:
            token_manager.set_token(token_value)
        except ValueError as exc:
            messagebox.showerror("Invalid Token", str(exc), parent=token_window)
            return

        token_window.grab_release()
        token_window.destroy()
        on_success()

    submit_button = ttk.Button(token_window, text="Submit", command=submit_token)
    submit_button.pack(pady=(0, 10))

    entry.bind("<Return>", submit_token)
    entry.focus_set()

    def on_close():
        root.destroy()

    token_window.protocol("WM_DELETE_WINDOW", on_close)


def run_gui():
    root = tk.Tk()
    root.withdraw()

    _prompt_for_token(root, lambda: _build_main_window(root))

    root.mainloop()


if __name__ == "__main__":
    run_gui()
