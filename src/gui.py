from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox

from src import ebay_api


session_token: Optional[str] = None


def start_token_window() -> None:
    """Launch the token entry window and transition to the main GUI."""

    token_window = tk.Tk()
    token_window.title("Enter eBay OAuth Token")

    tk.Label(token_window, text="Enter eBay OAuth Token").pack(pady=(15, 5), padx=15)

    entry = tk.Entry(token_window, width=60)
    entry.pack(padx=15)
    entry.focus_set()

    def submit_token() -> None:
        global session_token
        token = entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Token cannot be empty")
            return
        session_token = token
        print("Token entered and saved")
        token_window.destroy()
        launch_main_window()

    ttk.Button(token_window, text="Submit", command=submit_token).pack(pady=15)

    token_window.lift()
    token_window.attributes("-topmost", True)
    token_window.mainloop()


def _build_main_window(root: tk.Tk) -> None:
    """Main Watch Listings Fetcher window."""

    root.title("Watch Listings Fetcher")

    # Search fields
    tk.Label(root, text="Search Query").grid(row=0, column=0, sticky="w")
    search_query_entry = tk.Entry(root)
    search_query_entry.grid(row=0, column=1)

    tk.Label(root, text="Brand").grid(row=1, column=0, sticky="w")
    brand_entry = tk.Entry(root)
    brand_entry.grid(row=1, column=1)

    tk.Label(root, text="Model").grid(row=2, column=0, sticky="w")
    model_entry = tk.Entry(root)
    model_entry.grid(row=2, column=1)

    tk.Label(root, text="Min Price").grid(row=3, column=0, sticky="w")
    min_price_entry = tk.Entry(root)
    min_price_entry.grid(row=3, column=1)

    tk.Label(root, text="Max Price").grid(row=4, column=0, sticky="w")
    max_price_entry = tk.Entry(root)
    max_price_entry.grid(row=4, column=1)

    tk.Label(root, text="Condition").grid(row=5, column=0, sticky="w")
    condition_entry = tk.Entry(root)
    condition_entry.grid(row=5, column=1)

    tk.Label(root, text="Listing Type").grid(row=6, column=0, sticky="w")
    listing_type_entry = tk.Entry(root)
    listing_type_entry.grid(row=6, column=1)

    tk.Label(root, text="Auction Only").grid(row=7, column=0, sticky="w")
    auction_only_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Auction Only", variable=auction_only_var).grid(
        row=7, column=1, sticky="w"
    )

    tk.Label(root, text="Max Time Left").grid(row=8, column=0, sticky="w")
    max_time_entry = tk.Entry(root)
    max_time_entry.grid(row=8, column=1)

    tk.Label(root, text="Exclude Keywords").grid(row=9, column=0, sticky="w")
    exclude_entry = tk.Entry(root)
    exclude_entry.grid(row=9, column=1)

    tk.Label(root, text="Results").grid(row=10, column=0, sticky="w")
    results_entry = tk.Entry(root)
    results_entry.insert(0, "20")
    results_entry.grid(row=10, column=1)

    # Output box
    output = tk.Text(root, height=15, width=80)
    output.grid(row=12, column=0, columnspan=2, pady=10)

    def fetch_listings():
        if not session_token:
            messagebox.showerror("Error", "No token available. Please restart the application.")
            return
        query = {
            "search_query": search_query_entry.get().strip(),
            "brand": brand_entry.get().strip(),
            "model": model_entry.get().strip(),
            "min_price": min_price_entry.get().strip(),
            "max_price": max_price_entry.get().strip(),
            "condition": condition_entry.get().strip(),
            "listing_type": listing_type_entry.get().strip(),
            "auction_only": auction_only_var.get(),
            "max_time_left": max_time_entry.get().strip(),
            "exclude_keywords": exclude_entry.get().strip(),
            "limit": results_entry.get().strip(),
        }
        try:
            listings = ebay_api.fetch_listings(query, session_token)
            output.delete(1.0, tk.END)
            computed_query = query.get("computed_query")
            if computed_query:
                output.insert(tk.END, f"Search query: {computed_query}\n\n")
            else:
                output.insert(tk.END, "Search query: (none)\n\n")
            if not listings:
                output.insert(tk.END, "No listings found.\n")
            else:
                for item in listings:
                    output.insert(tk.END, f"{item}\n")
        except Exception as e:
            output.delete(1.0, tk.END)
            output.insert(tk.END, f"Error: {e}\n")

    ttk.Button(root, text="Fetch Listings", command=fetch_listings).grid(
        row=11, column=0, columnspan=2, pady=10
    )


def launch_main_window() -> None:
    root = tk.Tk()
    _build_main_window(root)
    root.mainloop()


def run() -> None:
    start_token_window()


if __name__ == "__main__":
    run()
