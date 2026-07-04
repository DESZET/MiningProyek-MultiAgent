"""Public schemas for gamification endpoints.

Any change here must be mirrored in frontend/src/types/gamification.ts.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class RecordAttemptRequest(BaseModel):
    """POST /gamification/record-attempt body."""

    quiz_id: str = Field(..., min_length=1, max_length=64)
    score: int = Field(..., ge=0, le=100)
    understanding_level: str = Field(..., min_length=1, max_length=16)


class StatsResponse(BaseModel):
    total_xp: int
    level: int
    xp_into_level: int
    xp_for_next_level: int
    current_streak: int
    longest_streak: int


class BadgeResponse(BaseModel):
    code: str
    label: str
    description: str
    icon: str
    unlocked_at: datetime | None = None


class RecordAttemptResponse(BaseModel):
    xp_earned: int
    daily_bonus_earned: int = 0
    leveled_up: bool
    new_level: int
    stats: StatsResponse
    newly_unlocked: list[BadgeResponse]


class HistoryItem(BaseModel):
    quiz_id: str
    score: int
    understanding_level: str
    xp_earned: int
    completed_at: datetime
    topic: str | None = None


class HistorySummary(BaseModel):
    total_quizzes: int
    average_score: int
    total_xp: int
    best_score: int
    worst_score: int
    most_recent_topic: str | None = None


class HistoryResponse(BaseModel):
    summary: HistorySummary
    items: list[HistoryItem]


class TrendPoint(BaseModel):
    date: date
    average_score: int
    attempt_count: int


class TopicMasteryItem(BaseModel):
    topic: str
    average_score: int
    attempt_count: int


class AnalyticsResponse(BaseModel):
    quiz_count: int
    average_score: int
    total_xp: int
    score_trend: list[TrendPoint]
    topic_mastery: list[TopicMasteryItem]


# ============================================================================
# §4.8 Batch 2 — Leaderboard + Weekly goal
# ============================================================================


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    total_xp: int
    level: int
    is_you: bool = False


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    # The requester's rank even when they're outside the returned top-N
    # (None when they have no recorded progress yet).
    you_rank: int | None = None


class WeeklyProgressResponse(BaseModel):
    completed: int
    target: int
    percent: int
    goal_met: bool
    remaining: int


# ============================================================================
# §4.8 Batch 2-B — Preferences + Material bookmarks
# ============================================================================

from typing import Literal, Optional


class PreferencesResponse(BaseModel):
    default_num_questions: int
    default_difficulty: str
    shuffle_options: bool
    weekly_goal: int
    favorite_topic: Optional[str] = None


class PreferencesUpdate(BaseModel):
    """All fields optional — a PATCH-style partial update."""

    default_num_questions: Optional[Literal[3, 5, 7, 10]] = None
    default_difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    shuffle_options: Optional[bool] = None
    weekly_goal: Optional[int] = Field(default=None, ge=1, le=50)
    favorite_topic: Optional[str] = Field(default=None, max_length=80)


class BookmarkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    material_text: str = Field(..., min_length=1, max_length=20_000)


class BookmarkItem(BaseModel):
    id: str
    title: str
    material_text: str
    created_at: datetime


class BookmarkListResponse(BaseModel):
    items: list[BookmarkItem]
