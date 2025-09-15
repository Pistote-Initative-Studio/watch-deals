import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Make sure your EBAY_APP_ID is set in .env or environment
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not EBAY_APP_ID:
    raise RuntimeError("EBAY_APP_ID not found. Set it in your .env or environment variables.")

def test_fetch():
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    params = {
        "OPERATION-NAME": "findItemsAdvanced",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": "seiko",
        "paginationInput.entriesPerPage": 5,
        "itemFilter(0).name": "Condition",
        "itemFilter(0).value": "3000",   # Used
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data = resp.json()
    items = data["findItemsAdvancedResponse"][0]["searchResult"][0].get("item", [])
    for item in items:
        title = item["title"][0]
        price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
        url = item["viewItemURL"][0]
        print(f"{title} - ${price} - {url}")

if __name__ == "__main__":
    test_fetch()
