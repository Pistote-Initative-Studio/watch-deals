"""In-memory storage for the eBay OAuth token used by the application."""

from __future__ import annotations

from typing import Optional

_token: Optional[str] = None


def set_token(token: str) -> None:
    """Persist the provided OAuth token for the lifetime of the process."""
    cleaned = token.strip()
    if not cleaned:
        raise ValueError("Token cannot be empty. Please paste a valid token.")

    global _token
    _token = cleaned


def get_token() -> str:
    """Return the current OAuth token, raising if one has not been provided."""
    if not _token:
        raise RuntimeError(
            "No eBay token is set. Restart the app and provide a token when prompted."
        )
    return _token
