"""Integration tests for POST /auth/google (Google login).

Google token verification and the DB data-layer are mocked here — these tests
cover the route wiring + the graceful-degradation contract, not Google's crypto
or the merge logic (the latter is exercised via the smoke test against a real DB).
"""

import pytest

from app.routes import auth as auth_routes
from app.services import auth_service, gamification_service
from app.utils.errors import ApiException, INVALID_GOOGLE_TOKEN

VALID_IDENTITY = {
    "sub": "108112233445566778899",
    "email": "siswa@example.com",
    "name": "Siswa Asahlagi",
    "picture": "https://lh3.googleusercontent.com/a/abc123",
}

LINKED_USER = {
    "id": "11111111-2222-3333-4444-555555555555",
    "email": "siswa@example.com",
    "name": "Siswa Asahlagi",
    "avatar_url": "https://lh3.googleusercontent.com/a/abc123",
    "device_id": "device-xyz",
}


def test_google_login_returns_503_when_not_configured(client, monkeypatch):
    """No GOOGLE_CLIENT_ID -> login is simply off (503), app stays in guest mode."""
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)

    res = client.post("/auth/google", json={"credential": "any-token"})

    assert res.status_code == 503
    assert res.json()["code"] == "AUTH_UNAVAILABLE"


def test_google_login_success_returns_profile(client, monkeypatch):
    """Valid credential -> verified identity is linked and the profile returned."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(auth_routes, "is_db_configured", lambda: True)
    monkeypatch.setattr(auth_service, "verify_google_credential", lambda cred: VALID_IDENTITY)

    captured = {}

    def _fake_link(**kwargs):
        captured.update(kwargs)
        return LINKED_USER

    monkeypatch.setattr(gamification_service, "link_google_identity", _fake_link)

    res = client.post(
        "/auth/google",
        json={"credential": "good-token", "device_id": "device-xyz"},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["id"] == LINKED_USER["id"]
    assert body["email"] == "siswa@example.com"
    assert body["name"] == "Siswa Asahlagi"
    assert body["device_id"] == "device-xyz"
    # The verified Google sub + the caller's device id reach the data layer.
    assert captured["google_sub"] == VALID_IDENTITY["sub"]
    assert captured["device_id"] == "device-xyz"


def test_google_login_rejects_invalid_token(client, monkeypatch):
    """A token that fails Google verification -> 401 INVALID_GOOGLE_TOKEN."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(auth_routes, "is_db_configured", lambda: True)

    def _reject(cred):
        raise ApiException(
            status_code=401,
            code=INVALID_GOOGLE_TOKEN,
            detail="Login Google gagal diverifikasi. Coba masuk lagi.",
        )

    monkeypatch.setattr(auth_service, "verify_google_credential", _reject)

    res = client.post("/auth/google", json={"credential": "tampered-token"})

    assert res.status_code == 401
    assert res.json()["code"] == "INVALID_GOOGLE_TOKEN"


def test_google_login_rejects_empty_credential(client, monkeypatch):
    """Empty credential is caught by Pydantic min_length validation (422)."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id.apps.googleusercontent.com")

    res = client.post("/auth/google", json={"credential": ""})

    assert res.status_code == 422
