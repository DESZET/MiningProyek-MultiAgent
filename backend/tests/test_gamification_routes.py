"""Integration tests for /gamification/* graceful-degradation contract.

The gamification feature must never take down the core quiz UX. When the
database is missing or unreachable, every gamification endpoint should answer
with 503 GAMIFICATION_UNAVAILABLE (not 500) so the frontend degrades quietly.
"""

import pytest
from sqlalchemy.exc import OperationalError

from app.routes import gamification as gamification_routes
from app.services import gamification_service, submit_coordinator


def test_stats_returns_503_when_db_not_configured(client, monkeypatch):
    """DATABASE_URL unset → feature is simply off (503, handled by _require_db)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    res = client.get("/gamification/stats", headers={"X-Device-Id": "dev-1"})

    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"


def test_stats_returns_503_when_db_unreachable(client, monkeypatch):
    """DATABASE_URL set but the database is down → still 503, never 500.

    This is the Neon-scaled-to-zero / wrong-host / network-down case: the
    connection fails at query time with OperationalError. Without the global
    handler this surfaced as a 500 and broke the graceful-degradation contract.
    """
    monkeypatch.setattr(gamification_routes, "is_db_configured", lambda: True)

    def _connection_fails(device_id: str):
        raise OperationalError("SELECT 1", None, Exception("could not connect to server"))

    monkeypatch.setattr(gamification_service, "get_stats", _connection_fails)

    res = client.get("/gamification/stats", headers={"X-Device-Id": "dev-1"})

    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"


def test_analytics_returns_503_when_db_unreachable(client, monkeypatch):
    """The same contract holds for the analytics endpoint the dashboard uses."""
    monkeypatch.setattr(gamification_routes, "is_db_configured", lambda: True)

    def _connection_fails(device_id: str):
        raise OperationalError("SELECT 1", None, Exception("could not connect to server"))

    monkeypatch.setattr(gamification_service, "get_analytics", _connection_fails)

    res = client.get("/gamification/analytics", headers={"X-Device-Id": "dev-1"})

    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"


def test_non_gamification_db_error_stays_500(client, monkeypatch):
    """The OperationalError->503 mapping is scoped to /gamification/*.

    A DB failure on any other endpoint must keep standard 500 INTERNAL_ERROR
    semantics, not be mislabeled as a gamification outage.
    """
    def _connection_fails(quiz_id, answers, time_taken_seconds):
        raise OperationalError("SELECT 1", None, Exception("could not connect to server"))

    monkeypatch.setattr(submit_coordinator, "process_submission", _connection_fails)

    res = client.post(
        "/quiz/submit",
        json={"quiz_id": "any", "answers": [], "time_taken_seconds": 0},
    )

    assert res.status_code == 500
    assert res.json()["code"] == "INTERNAL_ERROR"
