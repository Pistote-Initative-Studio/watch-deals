# src/config.py
"""
Application configuration and OAuth token management for the eBay APIs.
Replace this file in your repo (drop-in). It uses requests.HTTPBasicAuth
so we don't manually create a base64 header.
"""

from __future__ import annotations
import os
import time
import threading
from typing import Tuple, Dict
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
    raise EnvironmentError("EBAY_CLIENT_ID and EBAY_CLIENT_SECRET must be set in your .env file")

# Token endpoint & default scope (Browse API scope)
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
DEFAULT_SCOPE = "https://api.ebay.com/oauth/api_scope"

# Simple in-memory token cache + lock (thread-safe)
_TOKEN_CACHE: Dict[str, Tuple[str, float]] = {}  # scope -> (token, expires_at)
_TOKEN_LOCK = threading.Lock()


def _request_new_token(scope: str) -> Tuple[str, float]:
    """Request a new client_credentials token from eBay, return (token, expires_at)."""
    payload = {
        "grant_type": "client_credentials",
        "scope": scope,
    }

    # Use requests' HTTPBasicAuth to supply client_id:client_secret securely
    auth = HTTPBasicAuth(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Debug - do not print secrets; show only that we're sending a request
    print("DEBUG => Requesting new token for scope:", scope)

    resp = requests.post(TOKEN_URL, auth=auth, headers=headers, data=payload, timeout=10)

    print("DEBUG => Response status:", resp.status_code)
    # print first chunk to help debugging without exposing secrets
    print("DEBUG => Response (truncated):", (resp.text or "")[:400])

    if resp.status_code != 200:
        # bubble up useful error info
        raise Exception(f"❌ Token request failed: {resp.status_code}, {resp.text}")

    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("OAuth token response did not include access_token")

    # expires_in is seconds (may be missing / non-int)
    try:
        expires_in = int(data.get("expires_in", 0))
    except (TypeError, ValueError):
        expires_in = 0

    # refresh a minute early to avoid edge cases
    expires_at = time.time() + max(expires_in - 60, 0)
    return token, expires_at


def get_access_token(scope: str = DEFAULT_SCOPE) -> str:
    """
    Return a cached OAuth access token for the requested scope, refreshing if necessary.
    Usage: token = get_access_token()
    """
    with _TOKEN_LOCK:
        cached = _TOKEN_CACHE.get(scope)
        now = time.time()
        if cached:
            token, expires_at = cached
            if now < expires_at:
                # still valid
                return token

        token, expires_at = _request_new_token(scope)
        _TOKEN_CACHE[scope] = (token, expires_at)
        return token
