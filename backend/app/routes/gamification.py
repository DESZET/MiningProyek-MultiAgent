"""Gamification endpoints — XP, streak, level, history, achievements.

Identity is an anonymous device id sent in the `X-Device-Id` header
(generated client-side, stored in localStorage). No login required.

All endpoints require DATABASE_URL to be configured; otherwise they return
503 so the core quiz features keep working without a database.
"""

from __future__ import annotations

from fastapi import APIRouter, Header

from app.db.session import is_db_configured
from app.schemas.gamification import (
    AnalyticsResponse,
    BookmarkCreate,
    BookmarkItem,
    BookmarkListResponse,
    HistoryResponse,
    LeaderboardResponse,
    PreferencesResponse,
    PreferencesUpdate,
    RecordAttemptRequest,
    RecordAttemptResponse,
    StatsResponse,
    WeeklyProgressResponse,
)
from app.services import gamification_service
from app.utils.errors import ApiException

router = APIRouter(prefix="/gamification", tags=["gamification"])

GAMIFICATION_UNAVAILABLE = "GAMIFICATION_UNAVAILABLE"
DEVICE_ID_REQUIRED = "DEVICE_ID_REQUIRED"


def _require_db() -> None:
    if not is_db_configured():
        raise ApiException(
            status_code=503,
            code=GAMIFICATION_UNAVAILABLE,
            detail="Fitur progres belum aktif. Hubungi pengelola aplikasi.",
        )


def _require_device_id(x_device_id: str | None) -> str:
    if not x_device_id or not x_device_id.strip():
        raise ApiException(
            status_code=400,
            code=DEVICE_ID_REQUIRED,
            detail="Identitas perangkat tidak ditemukan. Muat ulang halaman.",
        )
    return x_device_id.strip()


@router.post("/record-attempt", response_model=RecordAttemptResponse)
def record_attempt_endpoint(
    req: RecordAttemptRequest,
    x_device_id: str | None = Header(default=None),
) -> RecordAttemptResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    result = gamification_service.record_attempt(
        device_id=device_id,
        quiz_id=req.quiz_id,
        score=req.score,
        understanding_level=req.understanding_level,
    )
    return RecordAttemptResponse(**result)


@router.get("/stats", response_model=StatsResponse)
def stats_endpoint(
    x_device_id: str | None = Header(default=None),
) -> StatsResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return StatsResponse(**gamification_service.get_stats(device_id))


@router.get("/history", response_model=HistoryResponse)
def history_endpoint(
    x_device_id: str | None = Header(default=None),
    limit: int = 10,
) -> HistoryResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    limit = max(1, min(limit, 50))
    return HistoryResponse(
        summary=gamification_service.get_history_summary(device_id),
        items=gamification_service.get_history(device_id, limit),
    )


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics_endpoint(
    x_device_id: str | None = Header(default=None),
) -> AnalyticsResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return AnalyticsResponse(**gamification_service.get_analytics(device_id))


@router.get("/achievements")
def achievements_endpoint(
    x_device_id: str | None = Header(default=None),
) -> list[dict]:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return gamification_service.get_achievements(device_id)


@router.get("/leaderboard", response_model=LeaderboardResponse)
def leaderboard_endpoint(
    x_device_id: str | None = Header(default=None),
    limit: int = 20,
) -> LeaderboardResponse:
    """§4.8 — top players by XP. Guests appear as 'Anonim'."""
    _require_db()
    device_id = _require_device_id(x_device_id)
    limit = max(1, min(limit, 100))
    return LeaderboardResponse(**gamification_service.get_leaderboard(device_id, limit))


@router.get("/weekly-progress", response_model=WeeklyProgressResponse)
def weekly_progress_endpoint(
    x_device_id: str | None = Header(default=None),
) -> WeeklyProgressResponse:
    """§4.8 — quizzes completed in the last 7 days vs the weekly target."""
    _require_db()
    device_id = _require_device_id(x_device_id)
    return WeeklyProgressResponse(**gamification_service.get_weekly_progress(device_id))


# --- §4.8 Batch 2-B: preferences + bookmarks (need migration 0005) ----------

BOOKMARK_NOT_FOUND = "BOOKMARK_NOT_FOUND"


@router.get("/preferences", response_model=PreferencesResponse)
def get_preferences_endpoint(
    x_device_id: str | None = Header(default=None),
) -> PreferencesResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return PreferencesResponse(**gamification_service.get_preferences(device_id))


@router.patch("/preferences", response_model=PreferencesResponse)
def update_preferences_endpoint(
    req: PreferencesUpdate,
    x_device_id: str | None = Header(default=None),
) -> PreferencesResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    changes = req.model_dump(exclude_none=True)
    return PreferencesResponse(
        **gamification_service.update_preferences(device_id, changes)
    )


@router.get("/bookmarks", response_model=BookmarkListResponse)
def list_bookmarks_endpoint(
    x_device_id: str | None = Header(default=None),
) -> BookmarkListResponse:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return BookmarkListResponse(items=gamification_service.list_bookmarks(device_id))


@router.post("/bookmarks", response_model=BookmarkItem)
def create_bookmark_endpoint(
    req: BookmarkCreate,
    x_device_id: str | None = Header(default=None),
) -> BookmarkItem:
    _require_db()
    device_id = _require_device_id(x_device_id)
    return BookmarkItem(
        **gamification_service.add_bookmark(device_id, req.title, req.material_text)
    )


@router.delete("/bookmarks/{bookmark_id}")
def delete_bookmark_endpoint(
    bookmark_id: str,
    x_device_id: str | None = Header(default=None),
) -> dict:
    _require_db()
    device_id = _require_device_id(x_device_id)
    if not gamification_service.delete_bookmark(device_id, bookmark_id):
        raise ApiException(
            status_code=404,
            code=BOOKMARK_NOT_FOUND,
            detail="Materi tersimpan tidak ditemukan.",
        )
    return {"deleted": True}
