import datetime

import pytest

from app.schemas.internal import QuestionInternal, QuizInternal
from app.schemas.quiz import Answer
from app.services.quiz_evaluator import evaluate
from app.utils.errors import ANSWERS_LENGTH_MISMATCH, INVALID_QUESTION_ID, ApiException


def make_quiz() -> QuizInternal:
    return QuizInternal(
        quiz_id="test-quiz-evaluator",
        questions=[
            QuestionInternal(
                id=1,
                question="Apa ibu kota Indonesia?",
                options=["Jakarta", "Bandung", "Surabaya", "Medan"],
                correct_option_index=0,
            ),
            QuestionInternal(
                id=2,
                question="Apa warna langit pada siang hari?",
                options=["Merah", "Biru", "Hijau", "Kuning"],
                correct_option_index=1,
            ),
            QuestionInternal(
                id=3,
                question="Berapa jumlah sisi segitiga?",
                options=["2", "3", "4", "5"],
                correct_option_index=1,
            ),
        ],
        generated_at=datetime.datetime.now(datetime.timezone.utc),
        source_material="",
    )


def test_evaluate_all_correct() -> None:
    quiz = make_quiz()
    answers = [
        Answer(question_id=1, selected_option_index=0),
        Answer(question_id=2, selected_option_index=1),
        Answer(question_id=3, selected_option_index=1),
    ]

    result = evaluate(quiz=quiz, answers=answers, time_taken_seconds=123)

    assert result.correct_count == 3
    assert result.wrong_count == 0
    assert result.unanswered_count == 0
    assert result.total_questions == 3
    assert result.score_percentage == 100
    assert result.time_taken_seconds == 123
    assert result.average_time_per_question == 41.0
    assert all(item.is_correct for item in result.question_results)


def test_evaluate_all_wrong() -> None:
    quiz = make_quiz()
    answers = [
        Answer(question_id=1, selected_option_index=1),
        Answer(question_id=2, selected_option_index=0),
        Answer(question_id=3, selected_option_index=0),
    ]

    result = evaluate(quiz=quiz, answers=answers, time_taken_seconds=60)

    assert result.correct_count == 0
    assert result.wrong_count == 3
    assert result.unanswered_count == 0
    assert result.score_percentage == 0
    assert result.time_taken_seconds == 60
    assert all(not item.is_correct for item in result.question_results)


def test_evaluate_with_unanswered_questions() -> None:
    quiz = make_quiz()
    answers = [
        Answer(question_id=1, selected_option_index=None),
        Answer(question_id=2, selected_option_index=1),
        Answer(question_id=3, selected_option_index=None),
    ]

    result = evaluate(quiz=quiz, answers=answers, time_taken_seconds=40)

    assert result.correct_count == 1
    assert result.wrong_count == 0
    assert result.unanswered_count == 2
    assert result.score_percentage == 33
    assert result.total_questions == 3
    assert result.time_taken_seconds == 40
    assert result.question_results[0].is_unanswered is True
    assert result.question_results[2].is_unanswered is True


def test_evaluate_answers_length_mismatch_raises() -> None:
    quiz = make_quiz()
    answers = [Answer(question_id=1, selected_option_index=0)]

    with pytest.raises(ApiException) as exc_info:
        evaluate(quiz=quiz, answers=answers, time_taken_seconds=10)

    assert exc_info.value.code == ANSWERS_LENGTH_MISMATCH


def test_evaluate_invalid_question_id_raises() -> None:
    quiz = make_quiz()
    answers = [
        Answer(question_id=1, selected_option_index=0),
        Answer(question_id=2, selected_option_index=1),
        Answer(question_id=99, selected_option_index=2),
    ]

    with pytest.raises(ApiException) as exc_info:
        evaluate(quiz=quiz, answers=answers, time_taken_seconds=10)

    assert exc_info.value.code == INVALID_QUESTION_ID


def test_evaluate_counts_sum_to_total() -> None:
    quiz = make_quiz()
    answers = [
        Answer(question_id=1, selected_option_index=0),
        Answer(question_id=2, selected_option_index=None),
        Answer(question_id=3, selected_option_index=2),
    ]

    result = evaluate(quiz=quiz, answers=answers, time_taken_seconds=90)

    assert result.correct_count + result.wrong_count + result.unanswered_count == result.total_questions
