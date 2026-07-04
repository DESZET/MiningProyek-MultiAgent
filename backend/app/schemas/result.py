"""Public result-related schemas — mirror API.md §5.1, 5.5.

These shapes are part of the HTTP contract. Any change here must be
reflected in:
- /API.md §5
- /frontend/src/types/result.ts
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UnderstandingLevel(str, Enum):
    """Lowercase English enum codes (language-agnostic). Frontend maps to
    Indonesian display labels via i18n.ts."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScoreSummary(BaseModel):
    score_percentage: int = Field(..., ge=0, le=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    unanswered_count: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=1)


class ChartData(BaseModel):
    correct: int = Field(..., ge=0)
    wrong: int = Field(..., ge=0)
    unanswered: int = Field(..., ge=0)


class QuestionReview(BaseModel):
    """Per-question review row shown on the result page.

    Includes the original question + options so the frontend can render a
    "what you got right / wrong" breakdown without re-fetching the quiz.
    """

    question_id: int
    type: str = "multiple_choice"
    question: str
    options: list[str] = Field(default_factory=list)
    selected_option_index: Optional[int] = None
    correct_option_index: Optional[int] = None
    is_correct: bool
    is_unanswered: bool
    # §6.2 matching review: prompts, answer bank, user's pairing, correct pairing.
    left_items: Optional[list[str]] = None
    right_items: Optional[list[str]] = None
    matches: Optional[list[int]] = None
    correct_matches: Optional[list[int]] = None


class QuizSubmitResponse(BaseModel):
    """POST /quiz/submit success response."""

    quiz_id: str
    score: ScoreSummary
    time_taken_seconds: int = Field(..., ge=0)
    understanding_level: UnderstandingLevel
    insight: str
    recommendation: str
    chart_data: ChartData
    submitted_at: datetime
    question_reviews: list[QuestionReview]
