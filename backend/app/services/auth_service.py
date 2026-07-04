"""Google login — verify Google ID tokens (Google Identity Services).

The frontend's GIS button returns a Google ID token (a signed JWT). We verify
it against Google's public keys and confirm the audience matches our OAuth
client id. No secret is involved — verification uses Google's published certs,
so the client secret never touches this backend.

OWNER: Ravi (login). Pairs with gamification_service.link_google_identity for
the data-layer side (Ariq review).
"""

from __future__ import annotations

import os

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.utils.errors import ApiException, INVALID_GOOGLE_TOKEN

# Google's accepted token issuers.
_VALID_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

# Lazily-created transport; caches Google's signing certs across calls.
_transport: google_requests.Request | None = None


def _get_transport() -> google_requests.Request:
    global _transport
    if _transport is None:
        _transport = google_requests.Request()
    return _transport


def get_client_id() -> str | None:
    """The OAuth Web client id used to validate the token audience."""
    return os.getenv("GOOGLE_CLIENT_ID", "").strip() or None


def is_google_login_configured() -> bool:
    """True if GOOGLE_CLIENT_ID is set (Google login available)."""
    return get_client_id() is not None


def verify_google_credential(credential: str) -> dict:
    """Verify a Google ID token and return the identity claims.

    Returns: {sub, email, name, picture}. Raises ApiException(401) if the token
    is invalid, expired, or issued for a different audience.
    """
    client_id = get_client_id()
    if client_id is None:
        # Caller should gate on is_google_login_configured() first; be defensive.
        raise ApiException(
            status_code=401,
            code=INVALID_GOOGLE_TOKEN,
            detail="Login Google belum dikonfigurasi.",
        )

    try:
        # Checks signature, expiry, and audience == client_id.
        info = id_token.verify_oauth2_token(credential, _get_transport(), client_id)
    except ValueError:
        raise ApiException(
            status_code=401,
            code=INVALID_GOOGLE_TOKEN,
            detail="Login Google gagal diverifikasi. Coba masuk lagi.",
        )

    if info.get("iss") not in _VALID_ISSUERS:
        raise ApiException(
            status_code=401,
            code=INVALID_GOOGLE_TOKEN,
            detail="Login Google gagal diverifikasi. Coba masuk lagi.",
        )

    return {
        "sub": info["sub"],
        "email": info.get("email"),
        "name": info.get("name"),
        "picture": info.get("picture"),
    }
