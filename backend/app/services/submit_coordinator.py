"""Submit pipeline orchestrator.

Per ARCHITECTURE.md §9: orchestrates the full submit flow —
get quiz from storage → evaluate → classify → insight → recommend → response.

Multi-Agent upgrade (AI_AGENT_IDEAS.md §Agent Insight):
    - insight & recommendation sekarang dihasilkan agent_insight (LLM),
      bukan rule-based template statis.
    - Fallback otomatis ke rule-based kalau LLM tidak tersedia.

This module is intentionally thin. It does NOT implement any business
logic; it just wires together the services that do.

OWNER: orchestrator (any backend dev — change with team agreement).
"""

from datetime import datetime, timezone

from app.schemas.internal import EvaluationResult
from app.schemas.quiz import Answer
from app.schemas.result import (
    ChartData,
    QuestionReview,
    QuizSubmitResponse,
    ScoreSummary,
)
from app.services import (
    agent_insight,
    insight_engine,
    quiz_evaluator,
    quiz_storage,
    recommendation_engine,
    understanding_classifier,
)
from app.utils.errors import ApiException, QUIZ_NOT_FOUND


def process_submission(
    quiz_id: str,
    answers: list[Answer],
    time_taken_seconds: int,
) -> QuizSubmitResponse:
    """End-to-end submit pipeline.

    Raises ApiException for any validation/business error. The route
    handler does not need to catch — the global exception handler in
    main.py converts ApiException into the JSON envelope.
    """
    quiz = quiz_storage.get_quiz(quiz_id)
    if quiz is None:
        raise ApiException(
            status_code=404,
            code=QUIZ_NOT_FOUND,
            detail="Kuis tidak ditemukan atau sudah kedaluwarsa. Mulai ulang dari halaman utama.",
        )

    eval_result: EvaluationResult = quiz_evaluator.evaluate(
        quiz=quiz,
        answers=answers,
        time_taken_seconds=time_taken_seconds,
    )
    level = understanding_classifier.classify(eval_result)

    # Agent Insight: LLM-powered insight + recommendation (dengan fallback rule-based)
    insight, recommendation = agent_insight.generate_insight_and_recommendation(
        level, eval_result
    )

    # Build per-question review by zipping evaluator output with stored question text.
    questions_by_id = {q.id: q for q in quiz.questions}
    question_reviews = [
        QuestionReview(
            question_id=r.question_id,
            type=questions_by_id[r.question_id].type,
            question=questions_by_id[r.question_id].question,
            options=list(questions_by_id[r.question_id].options or []),
            selected_option_index=r.selected_option_index,
            correct_option_index=r.correct_option_index,
            is_correct=r.is_correct,
            is_unanswered=r.is_unanswered,
            # §6.2 matching review payload (None for other types).
            left_items=questions_by_id[r.question_id].left_items,
            right_items=questions_by_id[r.question_id].right_items,
            matches=r.matches,
            correct_matches=r.correct_matches,
        )
        for r in eval_result.question_results
        if r.question_id in questions_by_id
    ]

    return QuizSubmitResponse(
        quiz_id=quiz_id,
        score=ScoreSummary(
            score_percentage=eval_result.score_percentage,
            correct_count=eval_result.correct_count,
            wrong_count=eval_result.wrong_count,
            unanswered_count=eval_result.unanswered_count,
            total_questions=eval_result.total_questions,
        ),
        time_taken_seconds=time_taken_seconds,
        understanding_level=level,
        insight=insight,
        recommendation=recommendation,
        chart_data=ChartData(
            correct=eval_result.correct_count,
            wrong=eval_result.wrong_count,
            unanswered=eval_result.unanswered_count,
        ),
        submitted_at=datetime.now(timezone.utc),
        question_reviews=question_reviews,
    )
