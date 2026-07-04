"""Pure XP / streak / level rules. No I/O, no DB — fully unit-testable.

OWNER: Desta (Logic) — mirrors the deterministic style of insight/recommendation.

These functions define the gamification math. The gamification service
(gamification_service.py) calls them and persists the results.
"""

from __future__ import annotations

from datetime import date

# ---- XP rules -------------------------------------------------------------

COMPLETION_BONUS = 20  # flat reward for finishing a quiz at all
STREAK_BONUS_PER_DAY = 5  # extra XP per consecutive day
STREAK_BONUS_CAP = 50  # streak bonus never exceeds this


def compute_xp(score_percentage: int, streak: int) -> int:
    """XP for one completed quiz.

    base (= score 0..100) + flat completion bonus + capped streak bonus.
    """
    score_percentage = max(0, min(100, score_percentage))
    streak_bonus = min(max(streak, 0) * STREAK_BONUS_PER_DAY, STREAK_BONUS_CAP)
    return score_percentage + COMPLETION_BONUS + streak_bonus


# ---- Level rules ----------------------------------------------------------
#
# XP required to REACH level L is 50 * (L-1) * L:
#   L2 = 100, L3 = 300, L4 = 600, L5 = 1000, ...
# Progressive curve so early levels come fast, later ones take effort.


def xp_threshold_for_level(level: int) -> int:
    """Cumulative XP needed to reach a given level (level 1 = 0)."""
    if level <= 1:
        return 0
    return 50 * (level - 1) * level


def level_for_xp(total_xp: int) -> int:
    """Highest level whose threshold is met by total_xp."""
    level = 1
    while xp_threshold_for_level(level + 1) <= total_xp:
        level += 1
    return level


def xp_into_level(total_xp: int) -> int:
    """XP accumulated within the current level."""
    return total_xp - xp_threshold_for_level(level_for_xp(total_xp))


def xp_for_next_level(total_xp: int) -> int:
    """XP span between current level and the next (for a progress bar)."""
    level = level_for_xp(total_xp)
    return xp_threshold_for_level(level + 1) - xp_threshold_for_level(level)


# ---- Streak rules ---------------------------------------------------------


def next_streak(current_streak: int, last_active: date | None, today: date) -> int:
    """Compute the streak after a quiz completed on `today`.

    - No prior activity -> 1
    - Same day as last -> unchanged (already counted today; min 1)
    - Exactly the next day -> +1
    - A gap of 2+ days -> reset to 1
    """
    if last_active is None:
        return 1
    delta = (today - last_active).days
    if delta <= 0:
        return current_streak if current_streak > 0 else 1
    if delta == 1:
        return current_streak + 1
    return 1
