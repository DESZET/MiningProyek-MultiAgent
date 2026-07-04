"""§4.8 Batch 2-B — preferences + bookmarks.

CRUD needs a live DB (not available in CI), so we cover the DB-independent logic
(invalid-id guard, weekly-goal fallback) directly and the feature-off contract
(503 when DATABASE_URL is unset) at the route level — matching the existing
gamification test style.
"""

from app.services import gamification_service as gs


# ---------------------------------------------------------------------------
# DB-independent logic
# ---------------------------------------------------------------------------

def test_delete_bookmark_rejects_invalid_uuid_without_db():
    # A malformed id is rejected before any DB access, so this is safe with no DB.
    assert gs.delete_bookmark("dev-1", "not-a-uuid") is False
    assert gs.delete_bookmark("dev-1", "") is False


def test_weekly_goal_falls_back_to_default_when_db_absent(monkeypatch):
    # No DATABASE_URL → reading the (nonexistent) preferences table fails; the
    # weekly-progress endpoint must still work using the default target.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert gs._safe_weekly_goal("dev-1") == gs.WEEKLY_GOAL_DEFAULT


# ---------------------------------------------------------------------------
# Route contract — feature-off → 503 (never 500), until migration 0005 + DB
# ---------------------------------------------------------------------------

def test_preferences_get_503_when_db_off(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    res = client.get("/gamification/preferences", headers={"X-Device-Id": "d1"})
    assert res.status_code == 503
    assert res.json()["code"] == "GAMIFICATION_UNAVAILABLE"


def test_bookmarks_list_503_when_db_off(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    res = client.get("/gamification/bookmarks", headers={"X-Device-Id": "d1"})
    assert res.status_code == 503


def test_bookmarks_create_503_when_db_off(client, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    res = client.post(
        "/gamification/bookmarks",
        headers={"X-Device-Id": "d1"},
        json={"title": "Bab 1", "material_text": "x" * 150},
    )
    assert res.status_code == 503


def test_preferences_patch_validates_num_questions(client, monkeypatch):
    # 422 from schema validation happens before the DB gate — an invalid count is
    # rejected regardless of DB state.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    res = client.patch(
        "/gamification/preferences",
        headers={"X-Device-Id": "d1"},
        json={"default_num_questions": 4},  # not in {3,5,7,10}
    )
    assert res.status_code == 422
