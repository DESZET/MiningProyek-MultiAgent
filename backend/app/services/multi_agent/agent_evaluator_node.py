"""Agent Evaluator — node LangGraph untuk nilai jawaban + analisis granular.

AI_AGENT_IDEAS.md §Agent Evaluator:
    - Input: soal + jawaban user (dari state)
    - Tugas: nilai jawaban + klasifikasi pemahaman + identifikasi topik lemah granular
    - Pakai Random Forest yang sudah ada untuk klasifikasi
    - Tambah analisis topik lemah per-subtopik (bukan hanya keseluruhan)
    - Output: EvaluatorOutput di AgentState
    - Flag needs_retry=True kalau score < 50 (trigger auto-retry question)
"""

from __future__ import annotations

import logging
import re

from app.services.multi_agent.state import AgentState, EvaluatorOutput

logger = logging.getLogger("asahlagi.evaluator")

# Threshold untuk trigger auto-retry question (AI_AGENT_IDEAS.md §Auto-Retry Question)
_RETRY_SCORE_THRESHOLD = 50


def _extract_subtopic_from_question(question_text: str) -> str:
    """Ekstrak subtopik kasar dari teks soal untuk analisis granular.

    Strategi: ambil kata benda/konsep utama dari soal (kata terpanjang non-stopword).
    """
    _STOP = {
        "yang", "dan", "di", "ke", "dari", "untuk", "adalah", "dengan",
        "pada", "ini", "itu", "atau", "tidak", "akan", "dalam", "berapa",
        "sebutkan", "jelaskan", "apakah", "bagaimana", "mengapa", "kapan",
        "dimana", "manakah", "berikut", "benar", "salah", "pernyataan",
        "lengkapi", "kalimat", "pasangkan", "istilah",
    }
    words = re.findall(r"[A-Za-zÀ-ÿ]{4,}", question_text.lower())
    candidates = [w for w in words if w not in _STOP]
    if not candidates:
        return "Umum"
    # Kembalikan kata terpanjang sebagai perkiraan konsep utama
    return max(candidates, key=len).capitalize()


def run(state: AgentState) -> AgentState:
    """LangGraph node: evaluate jawaban user, hasilkan EvaluatorOutput kaya."""
    log = list(state.get("agent_log", []))
    log.append("agent_evaluator: start")

    quiz_id = state.get("quiz_id")
    answers_raw = state.get("answers") or []
    time_taken = state.get("time_taken_seconds") or 0

    if not quiz_id:
        state["error"] = "quiz_id tidak tersedia untuk evaluasi."
        state["agent_log"] = log
        return state

    # Load quiz dari storage
    from app.services import quiz_storage
    quiz = quiz_storage.get_quiz(quiz_id)
    if quiz is None:
        state["error"] = "Kuis tidak ditemukan atau sudah kedaluwarsa."
        state["agent_log"] = log
        return state

    # Deserialisasi answers
    from app.schemas.quiz import Answer
    answers = []
    for a in answers_raw:
        try:
            answers.append(Answer(**a) if isinstance(a, dict) else a)
        except Exception:  # noqa: BLE001
            pass

    # Evaluasi dengan evaluator existing
    from app.services import quiz_evaluator
    try:
        eval_result = quiz_evaluator.evaluate(quiz, answers, time_taken)
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_evaluator: evaluation failed: %s", exc)
        state["error"] = f"Evaluasi gagal: {exc}"
        state["agent_log"] = log
        return state

    # Klasifikasi pemahaman dengan Random Forest
    from app.services import understanding_classifier
    level = understanding_classifier.classify(eval_result)

    # Analisis topik lemah granular (per-subtopik dari teks soal)
    questions_by_id = {q.id: q for q in quiz.questions}
    weak_topics: list[str] = []
    strong_topics: list[str] = []
    weak_question_ids: list[int] = []

    seen_topics: set[str] = set()
    for qr in eval_result.question_results:
        q = questions_by_id.get(qr.question_id)
        if q is None:
            continue
        subtopic = _extract_subtopic_from_question(q.question)
        if not qr.is_correct and not qr.is_unanswered:
            weak_question_ids.append(qr.question_id)
            if subtopic not in seen_topics:
                weak_topics.append(subtopic)
                seen_topics.add(subtopic)
        elif qr.is_correct:
            if subtopic not in seen_topics:
                strong_topics.append(subtopic)
                seen_topics.add(subtopic)

    # Adaptive difficulty untuk kuis berikutnya
    score = eval_result.score_percentage
    if score >= 85:
        adaptive_difficulty = "hard"
    elif score >= 55:
        adaptive_difficulty = "medium"
    else:
        adaptive_difficulty = "easy"

    needs_retry = score < _RETRY_SCORE_THRESHOLD and len(weak_question_ids) > 0

    evaluator_out: EvaluatorOutput = {
        "score_percentage": score,
        "correct_count": eval_result.correct_count,
        "wrong_count": eval_result.wrong_count,
        "unanswered_count": eval_result.unanswered_count,
        "total_questions": eval_result.total_questions,
        "time_taken_seconds": time_taken,
        "average_time_per_question": eval_result.average_time_per_question,
        "understanding_level": level.value,
        "weak_question_ids": weak_question_ids,
        "weak_topics": weak_topics[:5],
        "strong_topics": strong_topics[:5],
        "needs_retry": needs_retry,
        "adaptive_difficulty": adaptive_difficulty,
    }

    log.append(
        f"agent_evaluator: done — score={score}%, level={level.value}, "
        f"weak_topics={weak_topics[:3]}, needs_retry={needs_retry}"
    )

    # Simpan ke state juga untuk access oleh downstream agents
    state_update = {
        **state,
        "evaluator": evaluator_out,
        "agent_log": log,
    }
    # Propagate eval_result ke insight agent (simpan sebagai raw)
    state_update["_eval_result"] = eval_result  # type: ignore[typeddict-unknown-key]

    return state_update
