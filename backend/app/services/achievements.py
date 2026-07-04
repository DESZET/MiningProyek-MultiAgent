"""Deterministic achievement (badge) rules.

OWNER: Desta (Logic) — same rule-engine spirit as insight/recommendation.

Each badge has a stable `code` (stored in DB), an Indonesian `label` and
`description` for the UI, and a Lucide `icon` name (no emoji, per BRAND.md).
`check` decides whether the badge is earned given the current context.

To add a badge: append an AchievementDef. Existing users earn it the next
time they complete a quiz if the condition is met.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class AchievementContext:
    total_xp: int
    level: int
    current_streak: int
    longest_streak: int
    total_attempts: int
    last_score: int


@dataclass(frozen=True)
class AchievementDef:
    code: str
    label: str
    description: str
    icon: str  # Lucide icon name
    check: Callable[[AchievementContext], bool]


ACHIEVEMENTS: tuple[AchievementDef, ...] = (
    AchievementDef(
        "first_quiz",
        "Langkah Pertama",
        "Menyelesaikan kuis pertamamu",
        "Sparkles",
        lambda c: c.total_attempts >= 1,
    ),
    AchievementDef(
        "perfect_score",
        "Sempurna",
        "Meraih skor 100",
        "Star",
        lambda c: c.last_score >= 100,
    ),
    AchievementDef(
        "streak_3",
        "Konsisten",
        "Streak 3 hari berturut-turut",
        "Flame",
        lambda c: c.longest_streak >= 3,
    ),
    AchievementDef(
        "streak_7",
        "Tujuh Hari",
        "Streak 7 hari berturut-turut",
        "Flame",
        lambda c: c.longest_streak >= 7,
    ),
    AchievementDef(
        "level_5",
        "Naik Kelas",
        "Mencapai level 5",
        "TrendingUp",
        lambda c: c.level >= 5,
    ),
    AchievementDef(
        "ten_quizzes",
        "Rajin Mengasah",
        "Menyelesaikan 10 kuis",
        "Trophy",
        lambda c: c.total_attempts >= 10,
    ),
)

# Lookup for enriching DB rows (code -> definition) for the UI.
ACHIEVEMENTS_BY_CODE: dict[str, AchievementDef] = {a.code: a for a in ACHIEVEMENTS}


def evaluate(ctx: AchievementContext) -> list[str]:
    """Return the badge codes that should be unlocked given the context."""
    return [a.code for a in ACHIEVEMENTS if a.check(ctx)]
