from dotenv import load_dotenv
import os

# Load environment variables from a .env file if present
load_dotenv()

# eBay Application ID
EBAY_APP_ID = os.environ.get("EBAY_APP_ID")
