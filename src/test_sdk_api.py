from ebaysdk.finding import Connection as Finding
import requests

from config import EBAY_APP_ID, get_access_token

BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

def _preview_browse_items(access_token: str, keyword: str = "seiko", limit: int = 3) -> None:
    """Fetch a few Browse API results using the shared OAuth token."""

    response = requests.get(
        BROWSE_SEARCH_URL,
        params={"q": keyword, "limit": str(limit)},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    response.raise_for_status()

    items = response.json().get("itemSummaries", [])
    if not items:
        print("No Browse API items found.")
        return

    print("Browse API preview:")
    for item in items:
        title = item.get("title") or "Untitled item"
        price_info = item.get("price") or {}
        price = price_info.get("value")
        currency = price_info.get("currency")
        price_display = f"{price} {currency}" if price and currency else price or "N/A"
        url = item.get("itemWebUrl") or "No URL available"
        print(f"- {title} | {price_display} | {url}")


def test_sdk():
    access_token = get_access_token()
    api = Finding(appid=EBAY_APP_ID, config_file=None)

    response = api.execute('findItemsAdvanced', {
        'keywords': 'seiko',
        'itemFilter': [
            {'name': 'Condition', 'value': 'Used'},
            {'name': 'ListingType', 'value': 'Auction'}
        ],
        'paginationInput': {'entriesPerPage': 5}
    })

    items = response.dict().get('searchResult', {}).get('item', [])
    for item in items:
        title = item.get('title')
        price = item.get('sellingStatus', {}).get('currentPrice', {}).get('value')
        url = item.get('viewItemURL')
        print(f"{title} - ${price} - {url}")

    print()
    _preview_browse_items(access_token)

if __name__ == "__main__":
    test_sdk()
