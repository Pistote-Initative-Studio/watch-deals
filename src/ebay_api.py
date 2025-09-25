import requests
from src import token_manager


def fetch_listings(query: dict):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/json",
    }

    params = {}
    if query.get("brand"):
        params["q"] = query["brand"]
    if query.get("model"):
        params["q"] = params.get("q", "") + " " + query["model"]
    if query.get("min_price"):
        params["filter"] = f"price:[{query['min_price']}..]"
    if query.get("max_price"):
        if "filter" in params:
            params["filter"] += f",price:[..{query['max_price']}]"
        else:
            params["filter"] = f"price:[..{query['max_price']}]"
    if query.get("limit"):
        params["limit"] = query["limit"]

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise RuntimeError(f"eBay API error {resp.status_code}: {resp.text}")

    data = resp.json()
    items = []
    for item in data.get("itemSummaries", []):
        title = item.get("title", "No title")
        price = item.get("price", {}).get("value", "N/A")
        currency = item.get("price", {}).get("currency", "")
        items.append(f"{title} - {price} {currency}")

    return items
