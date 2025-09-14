"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# eBay Application ID
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not EBAY_APP_ID:
    raise EnvironmentError("EBAY_APP_ID environment variable is not set")

