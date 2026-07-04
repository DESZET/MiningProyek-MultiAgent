"""Pytest fixtures shared across test files."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.internal import EvaluationResult, QuestionInternal, QuestionResult, QuizInternal
from app.services import quiz_storage


@pytest.fixture()
def client() -> TestClient:
    """FastAPI TestClient. Resets in-memory storage before each test."""
    quiz_storage.clear_all()
    return TestClient(app)


@pytest.fixture()
def sample_quiz() -> QuizInternal:
    """A small, deterministic quiz for testing evaluator/classifier without
    needing the generator to be implemented."""
    return QuizInternal(
        quiz_id="test-quiz-001",
        questions=[
            QuestionInternal(
                id=1,
                question="Apa peran utama klorofil?",
                options=[
                    "Menyerap cahaya matahari",
                    "Menghasilkan oksigen",
                    "Menyimpan glukosa",
                    "Memecah air",
                ],
                correct_option_index=0,
            ),
            QuestionInternal(
                id=2,
                question="Di mana fotosintesis terjadi?",
                options=["Mitokondria", "Kloroplas", "Inti sel", "Ribosom"],
                correct_option_index=1,
            ),
        ],
        generated_at=datetime.now(timezone.utc),
        source_material="Fotosintesis adalah proses...",
    )


@pytest.fixture()
def sample_eval_result() -> EvaluationResult:
    """A pre-computed EvaluationResult Desta can use to test classifier/insight
    without depending on the evaluator implementation."""
    return EvaluationResult(
        correct_count=4,
        wrong_count=1,
        unanswered_count=0,
        total_questions=5,
        score_percentage=80,
        time_taken_seconds=240,
        average_time_per_question=48.0,
        question_results=[
            QuestionResult(
                question_id=i,
                selected_option_index=0,
                correct_option_index=0,
                is_correct=True,
                is_unanswered=False,
            )
            for i in range(1, 5)
        ]
        + [
            QuestionResult(
                question_id=5,
                selected_option_index=1,
                correct_option_index=2,
                is_correct=False,
                is_unanswered=False,
            )
        ],
    )
