"""Gamification persistence service.

Ties the pure XP/achievement engines to the database. Each public function
manages its own transaction via get_session().

OWNER: Ariq (data/persistence) + Desta (rules via xp_engine/achievements).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select, update

import uuid

from app.db.models import (
    Achievement,
    MaterialBookmark,
    QuizAttempt,
    User,
    UserPreference,
    UserStats,
)
from app.db.session import get_session
from app.services import achievements as ach
from app.services import quiz_storage
from app.services import xp_engine


def _get_or_create_user(session, device_id: str) -> User:
    user = session.scalar(select(User).where(User.device_id == device_id))
    if user is None:
        user = User(device_id=device_id)
        session.add(user)
        session.flush()  # assign user.id
        session.add(UserStats(user_id=user.id))
        session.flush()
    return user


def _get_or_create_stats(session, user_id) -> UserStats:
    stats = session.get(UserStats, user_id)
    if stats is None:
        stats = UserStats(user_id=user_id)
        session.add(stats)
        session.flush()
    return stats


def _stats_payload(stats: UserStats) -> dict:
    return {
        "total_xp": stats.total_xp,
        "level": stats.level,
        "xp_into_level": xp_engine.xp_into_level(stats.total_xp),
        "xp_for_next_level": xp_engine.xp_for_next_level(stats.total_xp),
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
    }


def record_attempt(
    device_id: str,
    quiz_id: str,
    score: int,
    understanding_level: str,
    today: date | None = None,
) -> dict:
    """Record a completed quiz: update XP/streak/level, unlock achievements.
    Grants +50 XP bonus for the first successful Daily Challenge of the day.
    """
    today = today or date.today()
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        stats = _get_or_create_stats(session, user.id)

        new_streak = xp_engine.next_streak(
            stats.current_streak, stats.last_active_date, today
        )
        xp_base = xp_engine.compute_xp(score, new_streak)
        xp_earned = xp_base

        # Daily Challenge bonus XP logic
        is_daily = quiz_id.startswith("daily-")
        daily_bonus_earned = 0
        if is_daily:
            # Check if this exact daily quiz has already been attempted by this user
            already_attempted = session.scalar(
                select(func.count(QuizAttempt.id))
                .where(QuizAttempt.user_id == user.id)
                .where(QuizAttempt.quiz_id == quiz_id)
            ) > 0
            
            if not already_attempted:
                daily_bonus_earned = 50
                xp_earned += daily_bonus_earned

        old_level = stats.level
        stats.total_xp += xp_earned
        stats.level = xp_engine.level_for_xp(stats.total_xp)
        stats.current_streak = new_streak
        stats.longest_streak = max(stats.longest_streak, new_streak)
        stats.last_active_date = today

        quiz = quiz_storage.get_quiz(quiz_id)
        topic = quiz.topic if quiz is not None else "Umum"

        session.add(
            QuizAttempt(
                user_id=user.id,
                quiz_id=quiz_id,
                score=score,
                understanding_level=understanding_level,
                xp_earned=xp_earned,
                topic=topic,
            )
        )
        session.flush()

        total_attempts = session.scalar(
            select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user.id)
        )

        ctx = ach.AchievementContext(
            total_xp=stats.total_xp,
            level=stats.level,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            total_attempts=total_attempts or 0,
            last_score=score,
        )
        earned_codes = ach.evaluate(ctx)

        already = set(
            session.scalars(
                select(Achievement.badge_code).where(Achievement.user_id == user.id)
            ).all()
        )
        newly_unlocked: list[dict] = []
        for code in earned_codes:
            if code in already:
                continue
            session.add(Achievement(user_id=user.id, badge_code=code))
            definition = ach.ACHIEVEMENTS_BY_CODE[code]
            newly_unlocked.append(
                {
                    "code": definition.code,
                    "label": definition.label,
                    "description": definition.description,
                    "icon": definition.icon,
                    "unlocked_at": None,
                }
            )

        return {
            "xp_earned": xp_earned,
            "daily_bonus_earned": daily_bonus_earned,
            "leveled_up": stats.level > old_level,
            "new_level": stats.level,
            "stats": _stats_payload(stats),
            "newly_unlocked": newly_unlocked,
        }


def get_stats(device_id: str) -> dict:
    """Return current stats for a device. Creates a fresh user if unseen."""
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        stats = _get_or_create_stats(session, user.id)
        return _stats_payload(stats)


def get_history(device_id: str, limit: int = 10) -> list[dict]:
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return []
        rows = session.scalars(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user.id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(limit)
        ).all()
        return [
            {
                "quiz_id": r.quiz_id,
                "score": r.score,
                "understanding_level": r.understanding_level,
                "xp_earned": r.xp_earned,
                "completed_at": r.completed_at,
                "topic": r.topic,
            }
            for r in rows
        ]


def get_history_summary(device_id: str) -> dict:
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return {
                "total_quizzes": 0,
                "average_score": 0,
                "total_xp": 0,
                "best_score": 0,
                "worst_score": 0,
                "most_recent_topic": None,
            }

        stats = _get_or_create_stats(session, user.id)
        
        # Get total count (no limit)
        total_count = session.scalar(
            select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user.id)
        ) or 0
        
        # Get recent attempts for stats (limit 50 for performance)
        attempts = session.scalars(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user.id)
            .order_by(QuizAttempt.completed_at.desc())
            .limit(50)
        ).all()

        if not attempts:
            return {
                "total_quizzes": total_count,
                "average_score": 0,
                "total_xp": stats.total_xp,
                "best_score": 0,
                "worst_score": 0,
                "most_recent_topic": None,
            }

        scores = [r.score for r in attempts]
        return {
            "total_quizzes": total_count,
            "average_score": round(sum(scores) / len(scores)),
            "total_xp": stats.total_xp,
            "best_score": max(scores),
            "worst_score": min(scores),
            "most_recent_topic": attempts[0].topic if attempts[0].topic else None,
        }


def get_analytics(device_id: str, days: int = 30) -> dict:
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return {
                "quiz_count": 0,
                "average_score": 0,
                "total_xp": 0,
                "score_trend": [],
                "topic_mastery": [],
            }

        stats = _get_or_create_stats(session, user.id)

        trend_rows = session.execute(
            select(
                func.date(QuizAttempt.completed_at).label("date"),
                func.round(func.avg(QuizAttempt.score)).label("average_score"),
                func.count(QuizAttempt.id).label("attempt_count"),
            )
            .where(QuizAttempt.user_id == user.id)
            .group_by(func.date(QuizAttempt.completed_at))
            .order_by(func.date(QuizAttempt.completed_at).desc())
            .limit(days)
        ).all()

        topic_rows = session.execute(
            select(
                QuizAttempt.topic,
                func.round(func.avg(QuizAttempt.score)).label("average_score"),
                func.count(QuizAttempt.id).label("attempt_count"),
            )
            .where(QuizAttempt.user_id == user.id)
            .group_by(QuizAttempt.topic)
            .order_by(func.count(QuizAttempt.id).desc())
        ).all()

        return {
            "quiz_count": session.scalar(
                select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user.id)
            )
            or 0,
            "average_score": session.scalar(
                select(func.round(func.avg(QuizAttempt.score))).where(QuizAttempt.user_id == user.id)
            )
            or 0,
            "total_xp": stats.total_xp,
            "score_trend": [
                {
                    "date": row.date,
                    "average_score": int(row.average_score or 0),
                    "attempt_count": int(row.attempt_count or 0),
                }
                for row in reversed(trend_rows)
            ],
            "topic_mastery": [
                {
                    "topic": row.topic or "Umum",
                    "average_score": int(row.average_score or 0),
                    "attempt_count": int(row.attempt_count or 0),
                }
                for row in topic_rows
            ],
        }


def get_achievements(device_id: str) -> list[dict]:
    """Return all badges with unlocked timestamps (locked ones have None)."""
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        unlocked: dict[str, object] = {}
        if user is not None:
            for row in session.scalars(
                select(Achievement).where(Achievement.user_id == user.id)
            ).all():
                unlocked[row.badge_code] = row.unlocked_at
        return [
            {
                "code": a.code,
                "label": a.label,
                "description": a.description,
                "icon": a.icon,
                "unlocked_at": unlocked.get(a.code),
            }
            for a in ach.ACHIEVEMENTS
        ]


def _merge_user(session, *, src: User, dst: User) -> None:
    """Fold guest row `src` into account `dst`: move attempts + badges, combine
    stats, then delete `src`. Used when a user logs in on a new device but the
    Google account already exists elsewhere."""
    session.execute(
        update(QuizAttempt).where(QuizAttempt.user_id == src.id).values(user_id=dst.id)
    )

    dst_badges = set(
        session.scalars(
            select(Achievement.badge_code).where(Achievement.user_id == dst.id)
        ).all()
    )
    for badge in session.scalars(
        select(Achievement).where(Achievement.user_id == src.id)
    ).all():
        if badge.badge_code in dst_badges:
            session.delete(badge)  # dst already has it; drop the duplicate
        else:
            badge.user_id = dst.id

    src_stats = session.get(UserStats, src.id)
    dst_stats = _get_or_create_stats(session, dst.id)
    if src_stats is not None:
        dst_stats.total_xp += src_stats.total_xp
        dst_stats.level = xp_engine.level_for_xp(dst_stats.total_xp)
        dst_stats.longest_streak = max(dst_stats.longest_streak, src_stats.longest_streak)
        dst_stats.current_streak = max(dst_stats.current_streak, src_stats.current_streak)
        if src_stats.last_active_date and (
            dst_stats.last_active_date is None
            or src_stats.last_active_date > dst_stats.last_active_date
        ):
            dst_stats.last_active_date = src_stats.last_active_date
        session.delete(src_stats)

    session.flush()
    session.delete(src)
    session.flush()


def link_google_identity(
    *,
    google_sub: str,
    email: str | None,
    name: str | None,
    avatar_url: str | None,
    device_id: str | None = None,
) -> dict:
    """Link a verified Google identity to an app user (find-or-create).

    - Account already exists for this google_sub: that row is canonical. If the
      caller's guest device row is different, merge its progress in.
    - No account yet: promote the caller's guest device row in place (zero data
      migration), or create a fresh user if there's no guest row.

    Returns {id, email, name, avatar_url, device_id} — device_id is the canonical
    identity the client should use for subsequent gamification calls.
    """
    with get_session() as session:
        account = session.scalar(select(User).where(User.google_sub == google_sub))
        guest = (
            session.scalar(select(User).where(User.device_id == device_id))
            if device_id
            else None
        )

        if account is None:
            if guest is not None:
                user = guest  # promote in place
            else:
                user = User(device_id=device_id or f"google:{google_sub}")
                session.add(user)
                session.flush()
                session.add(UserStats(user_id=user.id))
                session.flush()
            user.google_sub = google_sub
            user.email = email
            user.display_name = name
            user.avatar_url = avatar_url
        else:
            user = account
            # Refresh profile fields from the latest Google data.
            user.email = email or user.email
            user.display_name = name or user.display_name
            user.avatar_url = avatar_url or user.avatar_url
            if guest is not None and guest.id != account.id:
                _merge_user(session, src=guest, dst=account)

        session.flush()
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.display_name,
            "avatar_url": user.avatar_url,
            "device_id": user.device_id,
        }


# ============================================================================
# §4.8 Batch 2 — Leaderboard + Weekly goal (no new tables; reads existing data)
# ============================================================================

WEEKLY_GOAL_DEFAULT = 5
_ANON_NAME = "Anonim"


def _display_name(name: str | None) -> str:
    """Privacy: only logged-in users have a display name; guests show as Anonim."""
    cleaned = (name or "").strip()
    return cleaned or _ANON_NAME


def build_leaderboard_entries(
    rows: list[tuple[str, str | None, int, int]], device_id: str
) -> list[dict]:
    """Pure: shape ranked (device_id, display_name, total_xp, level) rows into
    leaderboard entries, flagging the requester. Ranks are 1-based by position."""
    return [
        {
            "rank": i + 1,
            "name": _display_name(display_name),
            "total_xp": total_xp,
            "level": level,
            "is_you": did == device_id,
        }
        for i, (did, display_name, total_xp, level) in enumerate(rows)
    ]


def weekly_summary(completed: int, target: int) -> dict:
    """Pure: weekly-goal progress payload from a completed count + target."""
    target = max(1, target)
    completed = max(0, completed)
    percent = min(100, round(completed / target * 100))
    return {
        "completed": completed,
        "target": target,
        "percent": percent,
        "goal_met": completed >= target,
        "remaining": max(0, target - completed),
    }


def get_leaderboard(device_id: str, limit: int = 20) -> dict:
    """Top players by XP. Only named (logged-in) users appear — anonymous guests
    are excluded so the board isn't flooded with 'Anonim' rows. Also returns the
    requester's own rank among named users (None if they're a guest)."""
    # A "named" user has a non-empty display_name (i.e. logged in).
    named = User.display_name.isnot(None) & (func.trim(User.display_name) != "")
    with get_session() as session:
        rows = session.execute(
            select(User.device_id, User.display_name, UserStats.total_xp, UserStats.level)
            .join(UserStats, User.id == UserStats.user_id)
            .where(named)
            .order_by(UserStats.total_xp.desc(), User.created_at.asc())
            .limit(limit)
        ).all()
        entries = build_leaderboard_entries(
            [(r.device_id, r.display_name, r.total_xp, r.level) for r in rows],
            device_id,
        )

        you_rank: int | None = None
        me = session.scalar(select(User).where(User.device_id == device_id))
        if me is not None and (me.display_name or "").strip():
            my_stats = session.get(UserStats, me.id)
            if my_stats is not None:
                higher = session.scalar(
                    select(func.count(UserStats.user_id))
                    .join(User, User.id == UserStats.user_id)
                    .where(named)
                    .where(UserStats.total_xp > my_stats.total_xp)
                )
                you_rank = (higher or 0) + 1

        return {"entries": entries, "you_rank": you_rank}


def _safe_weekly_goal(device_id: str) -> int:
    """Read the user's weekly_goal preference, falling back to the default if the
    preferences table doesn't exist yet (migration 0005 not applied) or the user
    has none. Kept separate so the weekly-progress endpoint — shipped before the
    preferences table — never hard-depends on it."""
    try:
        with get_session() as session:
            user = session.scalar(select(User).where(User.device_id == device_id))
            if user is None:
                return WEEKLY_GOAL_DEFAULT
            pref = session.get(UserPreference, user.id)
            return pref.weekly_goal if pref is not None else WEEKLY_GOAL_DEFAULT
    except Exception:  # noqa: BLE001 — table-missing etc.; default is always safe
        return WEEKLY_GOAL_DEFAULT


def get_weekly_progress(device_id: str, target: int | None = None) -> dict:
    """How many quizzes the user finished in the last 7 days vs their target."""
    if target is None:
        target = _safe_weekly_goal(device_id)
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        completed = 0
        if user is not None:
            since = datetime.now(timezone.utc) - timedelta(days=7)
            completed = (
                session.scalar(
                    select(func.count(QuizAttempt.id))
                    .where(QuizAttempt.user_id == user.id)
                    .where(QuizAttempt.completed_at >= since)
                )
                or 0
            )
        return weekly_summary(completed, target)


# ============================================================================
# §4.8 Batch 2-B — Preferences + Material bookmarks (need migration 0005)
# ============================================================================

_PREF_DEFAULTS = {
    "default_num_questions": 5,
    "default_difficulty": "medium",
    "shuffle_options": True,
    "weekly_goal": WEEKLY_GOAL_DEFAULT,
    "favorite_topic": None,
}


def _pref_payload(pref: UserPreference) -> dict:
    return {
        "default_num_questions": pref.default_num_questions,
        "default_difficulty": pref.default_difficulty,
        "shuffle_options": pref.shuffle_options,
        "weekly_goal": pref.weekly_goal,
        "favorite_topic": pref.favorite_topic,
    }


def get_preferences(device_id: str) -> dict:
    """Current learning preferences, or sensible defaults when none are stored."""
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        pref = session.get(UserPreference, user.id)
        return _pref_payload(pref) if pref is not None else dict(_PREF_DEFAULTS)


def update_preferences(device_id: str, changes: dict) -> dict:
    """Upsert the user's preferences with the provided (non-None) fields."""
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        pref = session.get(UserPreference, user.id)
        if pref is None:
            pref = UserPreference(user_id=user.id)
            session.add(pref)
        for key, value in changes.items():
            if value is not None:
                setattr(pref, key, value)
        session.flush()
        return _pref_payload(pref)


def _bookmark_payload(bm: MaterialBookmark) -> dict:
    return {
        "id": str(bm.id),
        "title": bm.title,
        "material_text": bm.material_text,
        "created_at": bm.created_at,
    }


def add_bookmark(device_id: str, title: str, material_text: str) -> dict:
    with get_session() as session:
        user = _get_or_create_user(session, device_id)
        bm = MaterialBookmark(
            user_id=user.id,
            title=title.strip()[:120],
            material_text=material_text[:20_000],
        )
        session.add(bm)
        session.flush()
        return _bookmark_payload(bm)


def list_bookmarks(device_id: str, limit: int = 100) -> list[dict]:
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return []
        rows = session.scalars(
            select(MaterialBookmark)
            .where(MaterialBookmark.user_id == user.id)
            .order_by(MaterialBookmark.created_at.desc())
            .limit(limit)
        ).all()
        return [_bookmark_payload(b) for b in rows]


def delete_bookmark(device_id: str, bookmark_id: str) -> bool:
    """Delete a bookmark the user owns. Returns False if not found / not theirs."""
    try:
        bm_uuid = uuid.UUID(bookmark_id)
    except (ValueError, AttributeError):
        return False
    with get_session() as session:
        user = session.scalar(select(User).where(User.device_id == device_id))
        if user is None:
            return False
        bm = session.get(MaterialBookmark, bm_uuid)
        if bm is None or bm.user_id != user.id:
            return False
        session.delete(bm)
        return True
