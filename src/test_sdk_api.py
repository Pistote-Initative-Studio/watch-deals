from ebaysdk.finding import Connection as Finding
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get your App ID (Client ID) from environment
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not EBAY_APP_ID:
    raise RuntimeError("Set your EBAY_APP_ID in .env")

def test_sdk():
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

if __name__ == "__main__":
    test_sdk()
