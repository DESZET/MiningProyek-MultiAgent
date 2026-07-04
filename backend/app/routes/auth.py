"""Auth endpoint — Google login via Google Identity Services.

Thin route (per ARCHITECTURE.md §5.2): verify the Google ID token, then hand
off to the data layer to link/create the user. Returns the profile + canonical
device id. Degrades to 503 when Google login or the database is not configured,
so the app keeps working in guest mode.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.db.session import is_db_configured
from app.schemas.auth import AuthUserResponse, GoogleLoginRequest
from app.services import auth_service, gamification_service
from app.utils.errors import ApiException, AUTH_UNAVAILABLE

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=AuthUserResponse)
def google_login_endpoint(req: GoogleLoginRequest) -> AuthUserResponse:
    """POST /auth/google — verify a Google ID token and return the app user."""
    if not auth_service.is_google_login_configured():
        raise ApiException(
            status_code=503,
            code=AUTH_UNAVAILABLE,
            detail="Login Google belum aktif. Hubungi pengelola aplikasi.",
        )
    if not is_db_configured():
        raise ApiException(
            status_code=503,
            code=AUTH_UNAVAILABLE,
            detail="Login belum tersedia. Hubungi pengelola aplikasi.",
        )

    identity = auth_service.verify_google_credential(req.credential)
    result = gamification_service.link_google_identity(
        google_sub=identity["sub"],
        email=identity["email"],
        name=identity["name"],
        avatar_url=identity["picture"],
        device_id=req.device_id,
    )
    return AuthUserResponse(**result)
