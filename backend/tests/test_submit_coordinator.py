from app.schemas.quiz import Answer
from app.services import quiz_storage, submit_coordinator


def test_process_submission_returns_valid_response(sample_quiz) -> None:
    # Ensure the quiz is stored so submit_coordinator can retrieve it.
    quiz_storage.clear_all()
    quiz_storage.save_quiz(sample_quiz)

    answers = [
        Answer(question_id=q.id, selected_option_index=q.correct_option_index)
        for q in sample_quiz.questions
    ]

    response = submit_coordinator.process_submission(
        quiz_id=sample_quiz.quiz_id,
        answers=answers,
        time_taken_seconds=100,
    )

    assert response.quiz_id == sample_quiz.quiz_id
    assert response.score.correct_count == len(sample_quiz.questions)
    assert response.score.wrong_count == 0
    assert response.score.unanswered_count == 0
    assert response.score.total_questions == len(sample_quiz.questions)
    assert response.score.score_percentage == 100
    assert response.time_taken_seconds == 100
    assert response.understanding_level.value in {"high", "medium", "low"}
    assert isinstance(response.insight, str) and response.insight
    assert isinstance(response.recommendation, str) and response.recommendation
    assert response.chart_data.correct == len(sample_quiz.questions)
    assert response.chart_data.wrong == 0
    assert response.chart_data.unanswered == 0


def test_process_submission_with_mixed_answers(sample_quiz) -> None:
    quiz_storage.clear_all()
    quiz_storage.save_quiz(sample_quiz)

    answers = [
        Answer(
            question_id=sample_quiz.questions[0].id,
            selected_option_index=sample_quiz.questions[0].correct_option_index,
        ),
        Answer(
            question_id=sample_quiz.questions[1].id,
            selected_option_index=None,
        ),
    ]

    response = submit_coordinator.process_submission(
        quiz_id=sample_quiz.quiz_id,
        answers=answers,
        time_taken_seconds=150,
    )

    assert response.score.correct_count == 1
    assert response.score.wrong_count == 0
    assert response.score.unanswered_count == 1
    assert response.score.total_questions == 2
    assert response.score.score_percentage == 50
    assert response.time_taken_seconds == 150
    assert response.understanding_level.value in {"high", "medium", "low"}
    assert isinstance(response.insight, str) and response.insight
    assert isinstance(response.recommendation, str) and response.recommendation
