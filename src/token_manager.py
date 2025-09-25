_token = None

def set_token(value: str) -> None:
    global _token
    _token = value

def get_token() -> str:
    if not _token:
        raise RuntimeError("No token set. Please restart and enter a token.")
    return _token
