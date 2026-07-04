"""§6.2 matching question type — generation + partial-credit evaluation."""

import pytest

from app.schemas.internal import QuestionInternal, QuizInternal
from app.schemas.quiz import Answer
from app.services import quiz_evaluator, quiz_generator
from datetime import datetime, timezone


_LONG_MATERIAL = (
    "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
    "dengan bantuan cahaya matahari dan klorofil. Mitokondria adalah organel "
    "tempat berlangsungnya respirasi seluler pada makhluk hidup. Ribosom "
    "berfungsi sebagai tempat sintesis protein di dalam sel. Kloroplas "
    "mengandung pigmen hijau yang menyerap energi cahaya matahari. Nukleus "
    "menyimpan materi genetik berupa kromosom yang mewariskan sifat. Vakuola "
    "menyimpan cadangan makanan dan menjaga tekanan turgor sel tumbuhan."
)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def test_rule_based_quiz_includes_one_matching_question(monkeypatch):
    from ml.generator import inference

    monkeypatch.setattr(inference, "is_available", lambda: False)
    quiz = quiz_generator.generate_quiz(_LONG_MATERIAL, num_questions=5)

    matching = [q for q in quiz.questions if q.type == "matching"]
    assert len(matching) == 1, "a large rule-based quiz should contain one matching question"

    m = matching[0]
    assert m.left_items and m.right_items and m.correct_matches
    assert len(m.left_items) == len(m.right_items) == len(m.correct_matches)
    assert 3 <= len(m.left_items) <= 4
    # correct_matches is a valid permutation of right-item indices.
    assert sorted(m.correct_matches) == list(range(len(m.right_items)))
    # The term must NOT appear verbatim in its own matched statement (blanked).
    for i, want in enumerate(m.correct_matches):
        assert m.left_items[i].lower() not in m.right_items[want].lower()


def test_matching_survives_dl_plus_rule_supplement(monkeypatch):
    """Regression: when DL underproduces and rule-based tops up, a matching
    question from the supplement must keep its left_items/right_items (they were
    being dropped by the combined.append in the supplement path)."""
    from ml.generator import inference

    # DL is "available" but only yields 2 MC questions (below target=5), forcing
    # the rule-based supplement that contributes the matching question.
    monkeypatch.setattr(inference, "is_available", lambda: True)
    monkeypatch.setattr(
        inference,
        "generate",
        lambda text, num_questions=None: [
            {
                "question": "Apa fungsi utama klorofil dalam tumbuhan hijau?",
                "options": ["Menyerap cahaya", "Menyimpan air", "Memecah gula", "Menahan panas"],
                "correct_option_index": 0,
            },
            {
                "question": "Di organel manakah respirasi seluler berlangsung?",
                "options": ["Nukleus", "Mitokondria", "Ribosom", "Vakuola"],
                "correct_option_index": 1,
            },
        ],
    )

    quiz = quiz_generator.generate_quiz(_LONG_MATERIAL, num_questions=5)
    matching = [q for q in quiz.questions if q.type == "matching"]
    assert matching, "supplement path should still include a matching question"
    for m in matching:
        assert m.left_items and m.right_items and m.correct_matches, (
            "matching pairing data must not be dropped in the supplement path"
        )
        assert len(m.left_items) == len(m.right_items) == len(m.correct_matches)


def test_matching_not_exposed_to_client():
    """to_public must hide correct_matches but expose the two lists to pair."""
    q = QuestionInternal(
        id=1,
        type="matching",
        question="Pasangkan",
        left_items=["A", "B", "C"],
        right_items=["x", "y", "z"],
        correct_matches=[2, 0, 1],
    )
    pub = q.to_public()
    assert pub.left_items == ["A", "B", "C"]
    assert pub.right_items == ["x", "y", "z"]
    assert not hasattr(pub, "correct_matches")


# ---------------------------------------------------------------------------
# Evaluation (partial credit)
# ---------------------------------------------------------------------------

def _matching_quiz() -> QuizInternal:
    return QuizInternal(
        quiz_id="m1",
        questions=[
            QuestionInternal(
                id=1,
                type="matching",
                question="Pasangkan",
                left_items=["A", "B", "C"],
                right_items=["da", "db", "dc"],
                correct_matches=[0, 1, 2],
            )
        ],
        generated_at=datetime.now(timezone.utc),
    )


def test_matching_all_correct_scores_100():
    quiz = _matching_quiz()
    res = quiz_evaluator.evaluate(quiz, [Answer(question_id=1, matches=[0, 1, 2])], 30)
    assert res.score_percentage == 100
    assert res.correct_count == 1 and res.wrong_count == 0


def test_matching_partial_credit_reflected_in_score():
    quiz = _matching_quiz()
    # 2 of 3 pairs correct → 67% on a single-question quiz.
    res = quiz_evaluator.evaluate(quiz, [Answer(question_id=1, matches=[0, 1, 0])], 30)
    assert res.score_percentage == 67
    # Not fully correct → counts as wrong, not correct.
    assert res.correct_count == 0 and res.wrong_count == 1
    assert res.unanswered_count == 0
    # Review carries the user + correct pairings.
    qr = res.question_results[0]
    assert qr.matches == [0, 1, 0]
    assert qr.correct_matches == [0, 1, 2]


def test_matching_unanswered_when_no_pairs():
    quiz = _matching_quiz()
    for matches in ([-1, -1, -1], None):
        res = quiz_evaluator.evaluate(
            quiz, [Answer(question_id=1, matches=matches)], 30
        )
        assert res.unanswered_count == 1
        assert res.correct_count == 0 and res.wrong_count == 0
        assert res.score_percentage == 0


def test_matching_mixes_with_other_types_in_score():
    quiz = QuizInternal(
        quiz_id="m2",
        questions=[
            QuestionInternal(
                id=1, type="matching", question="P",
                left_items=["A", "B", "C"], right_items=["da", "db", "dc"],
                correct_matches=[0, 1, 2],
            ),
            QuestionInternal(
                id=2, type="multiple_choice", question="Q",
                options=["a", "b", "c", "d"], correct_option_index=2,
            ),
        ],
        generated_at=datetime.now(timezone.utc),
    )
    answers = [
        Answer(question_id=1, matches=[0, 1, 0]),       # 2/3 → 0.667
        Answer(question_id=2, selected_option_index=2),  # correct → 1.0
    ]
    res = quiz_evaluator.evaluate(quiz, answers, 60)
    # (0.667 + 1) / 2 = 0.833 → 83%
    assert res.score_percentage == 83
    assert res.correct_count == 1  # only the MC is fully correct
    assert res.wrong_count == 1     # matching is partial → wrong bucket
