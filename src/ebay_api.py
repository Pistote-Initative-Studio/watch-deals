# src/ebay_api.py
import requests
from .config import get_access_token

def fetch_listings(query="seiko", limit=10):
    """
    Search eBay listings using Browse API.
    """
    token = get_access_token()

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit={limit}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.ok:
        return response.json()
    else:
        raise Exception(f"❌ API request failed: {response.status_code}, {response.text}")
