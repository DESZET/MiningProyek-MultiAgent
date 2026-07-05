"""Shared state schema untuk LangGraph multi-agent orchestrator.

AgentState adalah TypedDict yang menjadi single source of truth yang
mengalir melalui semua node di graph. Setiap agent membaca dari dan
menulis ke state ini.

Pola LangGraph: state immutable per step, direduce di setiap transisi.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class ExtractorOutput(TypedDict):
    """Output dari Agent Extractor."""
    clean_text: str
    language: str               # "id" | "en" | "unknown"
    estimated_topic: str
    sentence_count: int
    char_count: int
    is_summarized: bool         # True kalau materi panjang sudah di-summarize LLM
    quality_ok: bool
    quality_hint: Optional[str]


class QuizMakerOutput(TypedDict):
    """Output dari Agent Quiz Maker."""
    quiz_id: str
    questions: list[dict]       # serialized QuestionInternal
    total_questions: int
    difficulty: str
    topic: str
    polished: bool              # True kalau LLM polish berhasil
    validated: bool             # True kalau LLM validation lulus


class EvaluatorOutput(TypedDict):
    """Output dari Agent Evaluator — lebih kaya dari EvaluationResult."""
    score_percentage: int
    correct_count: int
    wrong_count: int
    unanswered_count: int
    total_questions: int
    time_taken_seconds: int
    average_time_per_question: float
    understanding_level: str    # "high" | "medium" | "low"
    weak_question_ids: list[int]
    weak_topics: list[str]      # granular per-subtopik
    strong_topics: list[str]
    needs_retry: bool           # True kalau score < 50 dan butuh auto-retry


class InsightOutput(TypedDict):
    """Output dari Agent Insight."""
    insight: str
    recommendation: str
    study_path: list[str]       # urutan topik yang disarankan
    adaptive_difficulty: str    # difficulty yang disarankan untuk kuis berikutnya


class AgentState(TypedDict):
    """Global state yang mengalir melalui seluruh graph.

    Field opsional (Optional) = belum diisi oleh agent sebelumnya.
    Field wajib = harus diisi sebelum graph dimulai.
    """
    # === INPUT ===
    # Untuk quiz generation flow
    raw_input: Optional[str]            # teks mentah / URL / path
    input_type: Optional[str]           # "text" | "url" | "pdf"
    difficulty: Optional[str]           # "easy" | "medium" | "hard" | None=adaptive
    num_questions: Optional[int]
    shuffle_options: bool
    device_id: Optional[str]

    # Untuk submit flow
    quiz_id: Optional[str]
    answers: Optional[list[dict]]       # serialized Answer
    time_taken_seconds: Optional[int]

    # Untuk chat flow
    chat_message: Optional[str]
    chat_history: Optional[list[dict]]

    # === AGENT OUTPUTS ===
    extractor: Optional[ExtractorOutput]
    quiz_maker: Optional[QuizMakerOutput]
    evaluator: Optional[EvaluatorOutput]
    insight: Optional[InsightOutput]

    # === FLOW CONTROL ===
    flow: str                           # "generate" | "submit" | "chat" | "adaptive"
    error: Optional[str]
    retry_count: int                    # berapa kali auto-retry sudah terjadi
    max_retries: int

    # === METADATA ===
    agent_log: list[str]               # audit trail: agent mana yang sudah jalan
