"""In-memory quiz store.

Implementation per ARCHITECTURE.md §7.1. Single-process, FIFO-evicted at
100 entries. Stores quizzes (with correct answers) keyed by quiz_id, so
that /quiz/submit can validate without trusting the client.

Migration path to SQLite is documented in ARCHITECTURE.md §7.2 — function
signatures here will not need to change.
"""

import json
import logging
from collections import OrderedDict
from typing import Optional

from app.db.models import PersistentQuiz
from app.db.session import get_session, is_db_configured
from app.schemas.internal import QuizInternal

logger = logging.getLogger(__name__)

_MAX_QUIZZES = 100
_store: "OrderedDict[str, QuizInternal]" = OrderedDict()


def save_quiz(quiz: QuizInternal) -> str:
    """Store a quiz, returning its quiz_id. Evicts oldest if over capacity.
    Saves to DB if configured, otherwise falls back gracefully to in-memory only.
    """
    _store[quiz.quiz_id] = quiz
    if len(_store) > _MAX_QUIZZES:
        _store.popitem(last=False)

    if is_db_configured():
        try:
            with get_session() as session:
                questions_data = [q.model_dump() for q in quiz.questions]
                pq = PersistentQuiz(
                    quiz_id=quiz.quiz_id,
                    source_material=quiz.source_material,
                    questions_json=json.dumps(questions_data),
                    difficulty=quiz.difficulty,
                    topic=quiz.topic,
                )
                session.merge(pq)
        except Exception as exc:
            logger.error("Failed to save quiz to DB gracefully: %s", exc)

    return quiz.quiz_id


def get_quiz(quiz_id: str) -> Optional[QuizInternal]:
    """Retrieve a quiz by id. Checks in-memory cache first, then DB."""
    # Check memory first
    quiz = _store.get(quiz_id)
    if quiz is not None:
        return quiz

    # Try DB if memory cache missed
    if is_db_configured():
        try:
            with get_session() as session:
                pq = session.get(PersistentQuiz, quiz_id)
                if pq is not None:
                    from app.schemas.internal import QuestionInternal
                    questions_data = json.loads(pq.questions_json)
                    questions = [QuestionInternal.model_validate(q) for q in questions_data]
                    quiz = QuizInternal(
                        quiz_id=pq.quiz_id,
                        questions=questions,
                        source_material=pq.source_material,
                        generated_at=pq.created_at,
                        difficulty=pq.difficulty,
                        topic=getattr(pq, "topic", "Umum"),
                    )
                    # Cache in memory for faster subsequent lookups
                    _store[quiz_id] = quiz
                    return quiz
        except Exception as exc:
            logger.error("Failed to get quiz from DB: %s", exc)

    return None


def clear_all() -> None:
    """Reset the store. Used by tests; do not call from production code."""
    _store.clear()

