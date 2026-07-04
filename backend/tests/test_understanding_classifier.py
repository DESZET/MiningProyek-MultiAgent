from app.services import recommendation_engine
from app.schemas.internal import EvaluationResult, QuestionResult
from app.schemas.result import UnderstandingLevel


def make_eval(score, time, correct=4, wrong=1, unanswered=0, total=5):
    return EvaluationResult(
        correct_count=correct,
        wrong_count=wrong,
        unanswered_count=unanswered,
        total_questions=total,
        score_percentage=score,
        time_taken_seconds=time,
        question_results=[
            QuestionResult(
                question_id=i, selected_option_index=0, correct_option_index=0,
                is_correct=True, is_unanswered=False
            ) for i in range(1, total + 1)
        ],
    )


def test_high_perfect_fast():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.HIGH, make_eval(score=100, time=200)
    )
    assert "lanjutan" in result.lower() or "berikutnya" in result.lower()


def test_high_slow():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.HIGH, make_eval(score=85, time=600)
    )
    assert "ragu" in result.lower() or "berikutnya" in result.lower()


def test_medium_many_unanswered():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.MEDIUM, make_eval(score=60, time=300, unanswered=2)
    )
    assert "asah lagi" in result.lower()


def test_medium_slow():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.MEDIUM, make_eval(score=55, time=600)
    )
    assert "asah lagi" in result.lower()


def test_medium_default():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.MEDIUM, make_eval(score=55, time=300)
    )
    assert "asah lagi" in result.lower()


def test_low_many_unanswered():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.LOW, make_eval(score=20, time=300, unanswered=3)
    )
    assert "asah lagi" in result.lower()


def test_low_very_low_score():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.LOW, make_eval(score=15, time=300)
    )
    assert "asah lagi" in result.lower()


def test_low_default():
    result = recommendation_engine.generate_recommendation(
        UnderstandingLevel.LOW, make_eval(score=35, time=300)
    )
    assert "asah lagi" in result.lower()