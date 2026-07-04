"""Unit tests for the pure XP / streak / level engine.

No DB needed — these lock down the gamification math.
"""

from datetime import date

from app.services import xp_engine


def test_compute_xp_base_plus_bonuses():
    # score 80 + completion 20 + streak(3*5=15) = 115
    assert xp_engine.compute_xp(80, 3) == 115


def test_compute_xp_streak_bonus_capped():
    # streak 100 -> bonus capped at 50; 100 + 20 + 50 = 170
    assert xp_engine.compute_xp(100, 100) == 170


def test_compute_xp_clamps_score():
    assert xp_engine.compute_xp(150, 0) == 120  # score clamped to 100 + 20
    assert xp_engine.compute_xp(-10, 0) == 20  # score clamped to 0 + 20


def test_level_thresholds():
    assert xp_engine.level_for_xp(0) == 1
    assert xp_engine.level_for_xp(99) == 1
    assert xp_engine.level_for_xp(100) == 2
    assert xp_engine.level_for_xp(299) == 2
    assert xp_engine.level_for_xp(300) == 3
    assert xp_engine.level_for_xp(600) == 4


def test_xp_into_and_for_next_level():
    # at 150 XP: level 2 (threshold 100), into=50, span to L3 = 300-100 = 200
    assert xp_engine.xp_into_level(150) == 50
    assert xp_engine.xp_for_next_level(150) == 200


def test_streak_first_activity():
    assert xp_engine.next_streak(0, None, date(2026, 5, 19)) == 1


def test_streak_consecutive_day():
    assert xp_engine.next_streak(2, date(2026, 5, 18), date(2026, 5, 19)) == 3


def test_streak_same_day_unchanged():
    assert xp_engine.next_streak(4, date(2026, 5, 19), date(2026, 5, 19)) == 4


def test_streak_gap_resets():
    assert xp_engine.next_streak(5, date(2026, 5, 10), date(2026, 5, 19)) == 1
