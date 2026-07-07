"""Multi-Agent Orchestrator — LangGraph StateGraph.

AI_AGENT_IDEAS.md §Fase 3 — Full Multi-Agent:
    - LangGraph StateGraph sebagai backbone
    - Setiap agent adalah node mandiri
    - Feedback loop: Evaluator → Quiz Maker (adaptive quiz & auto-retry)
    - Tiga flow utama: "generate", "submit", "adaptive"

Flow "generate":
    Extractor → Quiz Maker → END

Flow "submit":
    Evaluator → Insight → END
    (dengan kondisi: needs_retry → Quiz Maker → END)

Flow "adaptive":
    Extractor → Quiz Maker (difficulty dari Evaluator) → END

Diagram:
    generate:   [extractor] → [quiz_maker] → END
    submit:     [evaluator] → {needs_retry? → [quiz_maker], else → [insight]} → END
    adaptive:   [extractor] → [quiz_maker_adaptive] → END
"""

from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from app.services.multi_agent.state import AgentState
from app.services.multi_agent import (
    agent_extractor,
    agent_quiz_maker_node,
    agent_evaluator_node,
    agent_insight_node,
)

logger = logging.getLogger("asahlagi.orchestrator")

# ============================================================================
# Routing functions — menentukan edge berikutnya berdasarkan state
# ============================================================================


def _route_after_evaluator(state: AgentState) -> Literal["agent_insight", "agent_quiz_maker_retry"]:
    """Setelah evaluasi:
    - needs_retry=True → trigger Auto-Retry Question (quiz maker baru)
    - else → lanjut ke insight
    """
    evaluator = state.get("evaluator") or {}
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 1)

    if evaluator.get("needs_retry") and retry_count < max_retries:
        logger.info(
            "orchestrator: routing to auto-retry (score=%s%%, retry=%d/%d)",
            evaluator.get("score_percentage"),
            retry_count,
            max_retries,
        )
        return "agent_quiz_maker_retry"
    return "agent_insight"


def _route_after_extractor(state: AgentState) -> Literal["agent_quiz_maker", "__end__"]:
    """Setelah extractor: lanjut ke quiz maker kalau tidak ada error."""
    if state.get("error"):
        logger.warning("orchestrator: extractor error, ending: %s", state["error"])
        return "__end__"
    extractor = state.get("extractor", {})
    if not extractor.get("quality_ok"):
        return "__end__"
    return "agent_quiz_maker"


# ============================================================================
# Auto-Retry wrapper node
# ============================================================================


def _agent_quiz_maker_retry(state: AgentState) -> AgentState:
    """Auto-Retry Question: generate soal baru dari materi yang sama.

    AI_AGENT_IDEAS.md §Auto-Retry Question:
    'Kalau salah di soal tertentu, sistem otomatis generate soal baru
    dengan topik yang sama tapi dari sudut berbeda.'

    Menggunakan materi sumber yang sama tapi dengan difficulty lebih mudah
    dan memfokuskan pada topik yang lemah.
    """
    log = list(state.get("agent_log", []))
    evaluator = state.get("evaluator", {})
    retry_count = state.get("retry_count", 0)

    log.append(f"orchestrator: auto-retry #{retry_count + 1} — generating easier questions")

    # Set difficulty ke easy untuk retry (lebih mudah)
    new_state = {
        **state,
        "difficulty": "easy",
        "num_questions": min(3, state.get("num_questions", 5)),
        "retry_count": retry_count + 1,
        "agent_log": log,
        "flow": "adaptive",
    }

    # Pastikan ada extractor output (dari materi sebelumnya)
    # Jika tidak ada (misalnya flow submit langsung), gunakan topic dari quiz
    if not new_state.get("extractor") and new_state.get("quiz_id"):
        from app.services import quiz_storage
        quiz = quiz_storage.get_quiz(new_state["quiz_id"])
        if quiz and quiz.source_material:
            from app.services.material_quality import assess
            quality_ok, quality_hint = assess(quiz.source_material)
            new_state["extractor"] = {
                "clean_text": quiz.source_material,
                "language": "id",
                "estimated_topic": quiz.topic,
                "sentence_count": 0,
                "char_count": len(quiz.source_material),
                "is_summarized": False,
                "quality_ok": quality_ok,
                "quality_hint": quality_hint,
            }

    return agent_quiz_maker_node.run(new_state)


# ============================================================================
# Build graphs
# ============================================================================


def _build_generate_graph() -> StateGraph:
    """Graph untuk flow 'generate': Extractor → Quiz Maker."""
    g = StateGraph(AgentState)

    g.add_node("agent_extractor", agent_extractor.run)
    g.add_node("agent_quiz_maker", agent_quiz_maker_node.run)

    g.set_entry_point("agent_extractor")
    g.add_conditional_edges(
        "agent_extractor",
        _route_after_extractor,
        {"agent_quiz_maker": "agent_quiz_maker", "__end__": END},
    )
    g.add_edge("agent_quiz_maker", END)

    return g


def _build_submit_graph() -> StateGraph:
    """Graph untuk flow 'submit': Evaluator → (Retry | Insight)."""
    g = StateGraph(AgentState)

    g.add_node("agent_evaluator", agent_evaluator_node.run)
    g.add_node("agent_insight", agent_insight_node.run)
    g.add_node("agent_quiz_maker_retry", _agent_quiz_maker_retry)

    g.set_entry_point("agent_evaluator")
    g.add_conditional_edges(
        "agent_evaluator",
        _route_after_evaluator,
        {
            "agent_insight": "agent_insight",
            "agent_quiz_maker_retry": "agent_quiz_maker_retry",
        },
    )
    g.add_edge("agent_insight", END)
    g.add_edge("agent_quiz_maker_retry", END)

    return g


# Compile graphs sekali saja (singleton)
_generate_graph = _build_generate_graph().compile()
_submit_graph = _build_submit_graph().compile()


# ============================================================================
# Public API — dipanggil dari routes
# ============================================================================


def run_generate_flow(
    raw_input: str,
    input_type: str = "text",
    difficulty: str | None = None,
    num_questions: int = 5,
    shuffle_options: bool = True,
    device_id: str | None = None,
) -> AgentState:
    """Jalankan generate flow: Extractor → Quiz Maker.

    Return AgentState final. Caller ambil state["quiz_maker"] untuk response.
    """
    initial_state: AgentState = {
        "raw_input": raw_input,
        "input_type": input_type,
        "difficulty": difficulty,
        "num_questions": num_questions,
        "shuffle_options": shuffle_options,
        "device_id": device_id,
        "quiz_id": None,
        "answers": None,
        "time_taken_seconds": None,
        "chat_message": None,
        "chat_history": None,
        "extractor": None,
        "quiz_maker": None,
        "evaluator": None,
        "insight": None,
        "flow": "generate",
        "error": None,
        "retry_count": 0,
        "max_retries": 1,
        "agent_messages": [],
        "reextract_count": 0,
        "reevaluation_count": 0,
        "agent_log": [],
    }

    logger.info(
        "orchestrator: starting generate flow (input_type=%s, difficulty=%s, n=%d)",
        input_type, difficulty, num_questions,
    )

    final = _generate_graph.invoke(initial_state)
    logger.info("orchestrator: generate flow done — log=%s", final.get("agent_log", []))
    return final


def run_submit_flow(
    quiz_id: str,
    answers: list[dict],
    time_taken_seconds: int,
    device_id: str | None = None,
) -> AgentState:
    """Jalankan submit flow: Evaluator → (Retry | Insight).

    Return AgentState final. Caller ambil state["evaluator"] dan state["insight"].
    Kalau needs_retry, state["quiz_maker"] berisi kuis baru.
    """
    initial_state: AgentState = {
        "raw_input": None,
        "input_type": "text",
        "difficulty": None,
        "num_questions": 5,
        "shuffle_options": True,
        "device_id": device_id,
        "quiz_id": quiz_id,
        "answers": answers,
        "time_taken_seconds": time_taken_seconds,
        "chat_message": None,
        "chat_history": None,
        "extractor": None,
        "quiz_maker": None,
        "evaluator": None,
        "insight": None,
        "flow": "submit",
        "error": None,
        "retry_count": 0,
        "max_retries": 1,
        "agent_messages": [],
        "reextract_count": 0,
        "reevaluation_count": 0,
        "agent_log": [],
    }

    logger.info("orchestrator: starting submit flow (quiz_id=%s)", quiz_id)

    final = _submit_graph.invoke(initial_state)
    logger.info("orchestrator: submit flow done — log=%s", final.get("agent_log", []))
    return final
