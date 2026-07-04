"""Schemas for POST /chat — Asahi mascot game-dialog (see docs/CHATBOT.md).

Interaction is button-based: `intent` is a closed enum (no free-text input),
which keeps the prompt-injection surface tiny. The only semi-free field is
`weak_topics`, which is clamped in the service before reaching the model.
"""

from typing import Literal

from pydantic import BaseModel, Field

ChatIntent = Literal["opening", "weak_points", "study_tips", "encouragement"]
UnderstandingLevel = Literal["high", "medium", "low"]


class ChatContext(BaseModel):
    """The quiz result Asahi reacts to. Sent by the client from the result it
    already holds; still validated/clamped server-side."""

    quiz_id: str | None = Field(default=None, max_length=64)
    score_percentage: int = Field(ge=0, le=100)
    understanding_level: UnderstandingLevel
    correct_count: int = Field(ge=0, le=100)
    wrong_count: int = Field(ge=0, le=100)
    unanswered_count: int = Field(default=0, ge=0, le=100)
    weak_topics: list[str] = Field(default_factory=list, max_length=8)


class ChatRequest(BaseModel):
    intent: ChatIntent
    context: ChatContext


class ChatResponse(BaseModel):
    reply: str


# ── Free chat (open text box on the home page) ──────────────────────────────


class FreeChatMessage(BaseModel):
    role: Literal["user", "asahi"]
    # Asahi replies can be a few sentences; match the DB storage cap so restored
    # history validates when the client sends it back.
    content: str = Field(min_length=1, max_length=2000)


class FreeChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[FreeChatMessage] = Field(default_factory=list, max_length=20)


class FreeChatResponse(BaseModel):
    reply: str


class ChatHistoryResponse(BaseModel):
    messages: list[FreeChatMessage]
