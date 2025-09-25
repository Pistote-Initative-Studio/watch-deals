"""Application configuration and OAuth token management for the eBay APIs."""

from __future__ import annotations

import os
import threading
import time
import base64
from typing import Dict, Tuple

import requests
from dotenv import load_dotenv

# Load environment variables from a .env file if present.
load_dotenv()

# eBay OAuth2 token endpoint (Production)
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

# --------------------------------------------------------------------------------------
# Basic application configuration
# --------------------------------------------------------------------------------------

# eBay Application ID used by the legacy Finding API and SDK integrations.
EBAY_APP_ID = os.getenv("EBAY_APP_ID")

if not EBAY_APP_ID:
    raise EnvironmentError("EBAY_APP_ID environment variable is not set")

# OAuth client credentials used to obtain Browse API tokens.
EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

# Optional redirect URI for completeness when working with additional OAuth flows.
EBAY_REDIRECT_URI = os.getenv("EBAY_REDIRECT_URI")

# --------------------------------------------------------------------------------------
# OAuth token management
# --------------------------------------------------------------------------------------

_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_DEFAULT_SCOPE = "https://api.ebay.com/oauth/api_scope"

# Cache of access tokens keyed by scope.  Each entry stores ``(token, expires_at)``.
_TOKEN_CACHE: Dict[str, Tuple[str, float]] = {}
_TOKEN_LOCK = threading.Lock()


def _fetch_new_token(scope: str) -> Tuple[str, float]:
    if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
        raise EnvironmentError(
            "EBAY_CLIENT_ID and EBAY_CLIENT_SECRET environment variables must be set "
            "to request an OAuth access token."
        )

    # Build Basic Auth header
    basic_auth = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()

    response = requests.post(
        TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_auth}",
        },
        data={"grant_type": "client_credentials", "scope": scope},
        timeout=10,
    )

    response.raise_for_status()
    payload = response.json()

    token = payload.get("access_token")
    if not token:
        raise RuntimeError("OAuth token response did not include an access_token")

    try:
        expires_in = int(payload.get("expires_in", 0))
    except (TypeError, ValueError):
        expires_in = 0

    expires_at = time.time() + max(expires_in - 60, 0)
    return token, expires_at



def get_access_token():
    """
    Request an application access token using client_credentials grant.
    """
    import requests
    from requests.auth import HTTPBasicAuth

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        auth=HTTPBasicAuth(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET),
    )

    try:
        response.raise_for_status()
        token_info = response.json()
        return token_info["access_token"]
    except Exception:
        print("❌ Token request failed:")
        print("Status code:", response.status_code)
        print("Response body:", response.text)
        raise
