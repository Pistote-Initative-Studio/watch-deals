import tkinter as tk
from tkinter import ttk, messagebox

from src import token_manager
from src import ebay_api


def _prompt_for_token(root: tk.Tk, on_success) -> None:
    """Display a modal dialog requesting the user's eBay OAuth token."""

    token_window = tk.Toplevel(root)
    token_window.title("Enter eBay Token")

    tk.Label(token_window, text="Paste your eBay OAuth Token:").pack(pady=10)

    entry = tk.Entry(token_window, width=80)
    entry.pack(pady=5)

    def submit_token():
        token = entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Token cannot be empty")
            return
        token_manager.set_token(token)
        token_window.destroy()
        on_success()

    ttk.Button(token_window, text="Submit", command=submit_token).pack(pady=10)

    token_window.grab_set()              # make popup modal
    token_window.transient(root)         # keep popup on top
    token_window.lift()
    root.wait_window(token_window)


def _build_main_window(root: tk.Tk) -> None:
    """Main Watch Listings Fetcher window."""

    root.title("Watch Listings Fetcher")

    # Search fields
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
    condition_entry = tk.Entry(root)
    condition_entry.grid(row=4, column=1)

    tk.Label(root, text="Listing Type").grid(row=5, column=0, sticky="w")
    listing_type_entry = tk.Entry(root)
    listing_type_entry.grid(row=5, column=1)

    tk.Label(root, text="Max Time Left").grid(row=6, column=0, sticky="w")
    max_time_entry = tk.Entry(root)
    max_time_entry.grid(row=6, column=1)

    tk.Label(root, text="Exclude Keywords").grid(row=7, column=0, sticky="w")
    exclude_entry = tk.Entry(root)
    exclude_entry.grid(row=7, column=1)

    tk.Label(root, text="Results").grid(row=8, column=0, sticky="w")
    results_entry = tk.Entry(root)
    results_entry.insert(0, "20")
    results_entry.grid(row=8, column=1)

    # Output box
    output = tk.Text(root, height=15, width=80)
    output.grid(row=10, column=0, columnspan=2, pady=10)

    def fetch_listings():
        query = {
            "brand": brand_entry.get().strip(),
            "model": model_entry.get().strip(),
            "min_price": min_price_entry.get().strip(),
            "max_price": max_price_entry.get().strip(),
            "condition": condition_entry.get().strip(),
            "listing_type": listing_type_entry.get().strip(),
            "max_time_left": max_time_entry.get().strip(),
            "exclude_keywords": exclude_entry.get().strip(),
            "limit": results_entry.get().strip(),
        }
        try:
            listings = ebay_api.fetch_listings(query)
            output.delete(1.0, tk.END)
            if not listings:
                output.insert(tk.END, "No listings found.\n")
            else:
                for item in listings:
                    output.insert(tk.END, f"{item}\n")
        except Exception as e:
            output.delete(1.0, tk.END)
            output.insert(tk.END, f"Error: {e}\n")

    ttk.Button(root, text="Fetch Listings", command=fetch_listings).grid(row=9, column=0, columnspan=2, pady=10)


def run():
    root = tk.Tk()
    root.withdraw()  # hide until token entered

    def launch_main():
        root.deiconify()
        _build_main_window(root)

    _prompt_for_token(root, launch_main)
    root.mainloop()


if __name__ == "__main__":
    run()
