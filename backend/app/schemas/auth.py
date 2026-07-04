"""Pydantic schemas for Google login (OAuth — Google Identity Services).

The frontend obtains a Google ID token (JWT "credential") from the GIS button
and posts it here. The backend verifies it against Google's public keys and
links it to an app user. No password, no server-issued session token: the
frontend remembers the returned profile + device_id (see routes/auth.py).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class GoogleLoginRequest(BaseModel):
    """Body for POST /auth/google."""

    credential: str = Field(..., min_length=1, description="Google ID token from GIS")
    # The caller's current anonymous device id (localStorage). Used to carry
    # guest progress into the account on first login. Optional.
    device_id: str | None = Field(default=None, max_length=128)


class AuthUserResponse(BaseModel):
    """The logged-in user's profile plus the canonical device id the client
    should use for subsequent gamification calls."""

    id: str
    email: str | None
    name: str | None
    avatar_url: str | None
    # Canonical identity for gamification (X-Device-Id). After login the client
    # adopts this so the same Google account converges to one identity even
    # across devices.
    device_id: str
