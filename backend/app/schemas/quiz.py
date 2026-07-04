"""Public quiz-related schemas — mirror API.md §5.2-5.4.

These shapes are part of the HTTP contract. Any change here must be
reflected in:
- /API.md §5
- /frontend/src/types/quiz.ts
"""

from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, conlist

# §4.3 Quiz settings — shared field definitions reused across request bodies.
NumQuestions = Literal[3, 5, 7, 10]


QUESTION_TYPE_PATTERN = "^(multiple_choice|true_false|short_answer|matching)$"


class Question(BaseModel):
    """Quiz question as exposed over HTTP. No correct answer here — that lives in
    QuestionInternal (schemas/internal.py). For `matching`, the correct pairing
    (correct_matches) is also internal-only."""

    id: int = Field(..., ge=1)
    type: str = Field(default="multiple_choice", pattern=QUESTION_TYPE_PATTERN)
    question: str = Field(..., min_length=1)
    options: Optional[Annotated[list[str], conlist(str, min_length=2, max_length=4)]] = None
    # §6.2 matching: prompts (left) + shuffled answer bank (right). The correct
    # mapping is NOT exposed — only the two lists the user pairs up.
    left_items: Optional[list[str]] = None
    right_items: Optional[list[str]] = None


class Answer(BaseModel):
    """A user's answer for a single question."""

    question_id: int = Field(..., ge=1)
    selected_option_index: Optional[int] = Field(default=None, ge=0, le=3)
    text_answer: Optional[str] = Field(default=None)
    # §6.2 matching: matches[i] = chosen right_items index for left_items[i],
    # or -1 when that row is left unpaired.
    matches: Optional[list[int]] = Field(default=None)


class QuizGenerateRequest(BaseModel):
    """POST /quiz/generate request body."""

    material_text: str = Field(..., min_length=1, max_length=20_000)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    # §4.3 Quiz settings (pre-generate)
    num_questions: Optional[NumQuestions] = Field(default=None)
    shuffle_options: bool = Field(default=True)


class QuizGenerateFromUrlRequest(BaseModel):
    """POST /quiz/generate-from-url request body."""

    url: str = Field(..., min_length=1, max_length=2048)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    # §4.3 Quiz settings (pre-generate)
    num_questions: Optional[NumQuestions] = Field(default=None)
    shuffle_options: bool = Field(default=True)


class QuizGenerateResponse(BaseModel):
    """POST /quiz/generate success response."""

    quiz_id: str
    questions: list[Question]
    total_questions: int = Field(..., ge=1)
    generated_at: datetime
    difficulty: str = Field(default="medium")


class QuizSubmitRequest(BaseModel):
    """POST /quiz/submit request body."""

    quiz_id: str
    answers: list[Answer]
    time_taken_seconds: int = Field(..., ge=0, le=7200)


class QuizRegenerateRequest(BaseModel):
    """POST /quiz/regenerate request body."""

    quiz_id: str
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
