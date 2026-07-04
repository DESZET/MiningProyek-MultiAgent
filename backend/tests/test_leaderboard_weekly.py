"""§4.8-A — leaderboard + weekly goal.

The DB query layer follows the existing graceful-degradation contract (503 when
DATABASE_URL is unset), tested at the route level. The shaping/ranking logic is
extracted into pure helpers and unit-tested directly.
"""

from sqlalchemy.exc import OperationalError

from app.routes import gamification as gamification_routes
from app.services import gamification_service as gs


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_build_leaderboard_entries_ranks_and_flags_you():
    rows = [
        ("dev-a", "Alice", 300, 4),
        ("dev-b", None, 200, 3),       # guest → Anonim
        ("dev-me", "Me", 100, 2),
    ]
    entries = gs.build_leaderboard_entries(rows, device_id="dev-me")
    assert [e["rank"] for e in entries] == [1, 2, 3]
    assert entries[1]["name"] == "Anonim"
    assert entries[0]["is_you"] is False
    assert entries[2]["is_you"] is True


def test_weekly_summary_partial():
    s = gs.weekly_summary(completed=2, target=5)
    assert s == {
        "completed": 2,
        "target": 5,
        "percent": 40,
        "goal_met": False,
        "remaining": 3,
    }


def test_weekly_summary_met_is_capped_at_100():
    s = gs.weekly_summary(completed=8, target=5)
    assert s["percent"] == 100
    assert s["goal_met"] is True
    assert s["remaining"] == 0


def test_weekly_summary_guards_zero_target():
    # Should never divide by zero even if a bad target sneaks in.
    s = gs.weekly_summary(completed=1, target=0)
    assert s["target"] == 1 and s["goal_met"] is True


# ---------------------------------------------------------------------------
# Route contract — feature-off / DB-down → 503, never 500
# ---------------------------------------------------------------------------

def test_leaderboard_503_when_db_not_configured(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    res = client.get("/gamification/leaderboard", headers={"X-Device-Id": "d1"})
    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"


def test_weekly_progress_503_when_db_unreachable(client, monkeypatch):
    monkeypatch.setattr(gamification_routes, "is_db_configured", lambda: True)

    def _down(device_id, *a, **k):
        raise OperationalError("SELECT 1", None, Exception("could not connect"))

    monkeypatch.setattr(gs, "get_weekly_progress", _down)
    res = client.get("/gamification/weekly-progress", headers={"X-Device-Id": "d1"})
    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"
