"""Shared state schema untuk LangGraph multi-agent orchestrator.

AgentState adalah TypedDict yang menjadi single source of truth yang
mengalir melalui semua node di graph. Setiap agent membaca dari dan
menulis ke state ini.

Komunikasi dua arah antar agent:
    - Extractor ↔ Quiz Maker: Quiz Maker bisa request re-extract kalau soal < minimum
    - Evaluator ↔ Insight: Insight bisa request re-evaluate kalau data tidak konsisten
    - Insight ↔ Extractor: Insight bisa minta metadata topik dari Extractor
    - Quiz Maker ↔ Evaluator: Quiz Maker baca adaptive_difficulty dari Evaluator

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
    is_summarized: bool
    quality_ok: bool
    quality_hint: Optional[str]
    # Dua arah: feedback dari Quiz Maker untuk re-extract
    needs_reextract: bool       # True kalau Quiz Maker minta materi lebih banyak
    reextract_reason: Optional[str]


class QuizMakerOutput(TypedDict):
    """Output dari Agent Quiz Maker."""
    quiz_id: str
    questions: list[dict]
    total_questions: int
    difficulty: str
    topic: str
    polished: bool
    validated: bool
    # Dua arah: feedback ke Extractor kalau butuh re-extract
    requested_reextract: bool   # True kalau minta Extractor re-run
    questions_below_minimum: bool


class EvaluatorOutput(TypedDict):
    """Output dari Agent Evaluator."""
    score_percentage: int
    correct_count: int
    wrong_count: int
    unanswered_count: int
    total_questions: int
    time_taken_seconds: int
    average_time_per_question: float
    understanding_level: str
    weak_question_ids: list[int]
    weak_topics: list[str]
    strong_topics: list[str]
    needs_retry: bool
    adaptive_difficulty: str
    # Dua arah: feedback dari Insight untuk re-evaluate
    needs_reevaluation: bool    # True kalau Insight minta data lebih detail
    topic_context: Optional[str]  # Konteks topik dari Extractor


class InsightOutput(TypedDict):
    """Output dari Agent Insight."""
    insight: str
    recommendation: str
    study_path: list[str]
    adaptive_difficulty: str
    # Dua arah: bisa request re-evaluation ke Evaluator
    requested_reevaluation: bool  # True kalau Insight minta Evaluator re-run
    reevaluation_reason: Optional[str]
    # Dua arah: enrichment dari Extractor metadata
    topic_enriched: bool        # True kalau Insight dapat konteks dari Extractor


class AgentState(TypedDict):
    """Global state yang mengalir melalui seluruh graph."""
    # === INPUT ===
    raw_input: Optional[str]
    input_type: Optional[str]
    difficulty: Optional[str]
    num_questions: Optional[int]
    shuffle_options: bool
    device_id: Optional[str]

    # Untuk submit flow
    quiz_id: Optional[str]
    answers: Optional[list[dict]]
    time_taken_seconds: Optional[int]

    # Untuk chat flow
    chat_message: Optional[str]
    chat_history: Optional[list[dict]]

    # === AGENT OUTPUTS ===
    extractor: Optional[ExtractorOutput]
    quiz_maker: Optional[QuizMakerOutput]
    evaluator: Optional[EvaluatorOutput]
    insight: Optional[InsightOutput]

    # === KOMUNIKASI DUA ARAH antar agent ===
    # Pesan dari agent ke agent lain (message passing)
    agent_messages: list[dict]  # [{"from": "insight", "to": "evaluator", "msg": "..."}]

    # === FLOW CONTROL ===
    flow: str
    error: Optional[str]
    retry_count: int
    max_retries: int
    # Dua arah flow control
    reextract_count: int        # berapa kali Extractor sudah di-rerun
    reevaluation_count: int     # berapa kali Evaluator sudah di-rerun

    # === METADATA ===
    agent_log: list[str]
