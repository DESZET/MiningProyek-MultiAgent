"""Agent Quiz Maker — node LangGraph untuk generate + polish + validasi soal.

AI_AGENT_IDEAS.md §Agent Quiz Maker:
    - Tahap 1: IndoT5 / rule-based generate soal (lewat quiz_generator existing)
    - Tahap 2: LLM polish — perbaiki grammar, pastikan distractor masuk akal
    - Tahap 3: LLM validasi — apakah soal terjawab dari materi?
    - Output: QuizMakerOutput di AgentState

Menerima state.extractor.clean_text sebagai input.
Mendukung adaptive difficulty dari state.evaluator (untuk adaptive quiz flow).
"""

from __future__ import annotations

import json
import logging
import os

import httpx

from app.services.multi_agent.state import AgentState, QuizMakerOutput

logger = logging.getLogger("asahlagi.quiz_maker")

_API_URL = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"
_TIMEOUT_S = 30.0

_VALIDATE_SYSTEM_PROMPT = """\
Kamu adalah validator soal kuis bahasa Indonesia. 
Tugasmu: cek apakah setiap soal BISA DIJAWAB dari materi sumber yang diberikan.

Untuk setiap soal, tentukan:
- "ok": soal jelas dan bisa dijawab dari materi
- "fix": soal perlu perbaikan kecil (tulis versi perbaikannya)
- "drop": soal tidak bisa dijawab dari materi sama sekali

OUTPUT FORMAT JSON array:
[{"id": <int>, "status": "ok"|"fix"|"drop", "fixed_question": "<string atau null>"}]

ATURAN: Output HANYA JSON array. Tanpa penjelasan."""


def _validate_questions(questions: list[dict], material: str) -> dict[int, dict]:
    """Validasi soal dengan LLM. Return dict {id: {status, fixed_question}}."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {}

    items = [{"id": q["id"], "question": q["question"]} for q in questions]
    prompt = (
        f"MATERI:\n{material[:1000]}\n\n"
        f"SOAL:\n{json.dumps(items, ensure_ascii=False)}\n\n"
        "Validasi setiap soal."
    )
    try:
        resp = httpx.post(
            _API_URL,
            headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": _VALIDATE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 400,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
        if text.startswith("```"):
            text = "\n".join(l for l in text.splitlines() if not l.startswith("```")).strip()
        data = json.loads(text)
        return {item["id"]: item for item in data if isinstance(item, dict)}
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_quiz_maker_node: validation failed: %s", exc)
        return {}


def run(state: AgentState) -> AgentState:
    """LangGraph node: generate + polish + validate soal dari extractor output."""
    log = list(state.get("agent_log", []))
    log.append("agent_quiz_maker: start")

    extractor = state.get("extractor")
    if not extractor or not extractor.get("quality_ok"):
        hint = extractor.get("quality_hint", "Materi tidak memenuhi syarat.") if extractor else "Extractor belum berjalan."
        state["error"] = hint
        state["agent_log"] = log
        return state

    material = extractor["clean_text"]

    # Adaptive difficulty: ambil dari evaluator kalau ada (adaptive quiz flow)
    difficulty = state.get("difficulty") or "medium"
    evaluator = state.get("evaluator")
    if evaluator and state.get("flow") == "adaptive":
        difficulty = evaluator.get("adaptive_difficulty", difficulty)
        log.append(f"agent_quiz_maker: adaptive difficulty={difficulty}")

    num_questions = state.get("num_questions") or 5
    shuffle_options = state.get("shuffle_options", True)
    topic = extractor.get("estimated_topic", "Umum")

    # Tahap 1: Generate soal (existing quiz_generator + agent_quiz_maker polish)
    try:
        from app.services import quiz_generator
        quiz_internal = quiz_generator.generate_quiz(
            material_text=material,
            difficulty=difficulty,
            topic=topic,
            num_questions=num_questions,
            shuffle_options=shuffle_options,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_quiz_maker_node: generation failed: %s", exc)
        state["error"] = f"Gagal generate soal: {exc}"
        state["agent_log"] = log
        return state

    # Serialize soal
    questions_raw = []
    for q in quiz_internal.questions:
        questions_raw.append({
            "id": q.id,
            "type": q.type,
            "question": q.question,
            "options": list(q.options) if q.options else None,
            "correct_option_index": q.correct_option_index,
            "correct_answer_text": q.correct_answer_text,
            "left_items": list(q.left_items) if q.left_items else None,
            "right_items": list(q.right_items) if q.right_items else None,
            "correct_matches": list(q.correct_matches) if q.correct_matches else None,
        })

    # Tahap 3: LLM Validasi soal
    validated = False
    validation_map = _validate_questions(questions_raw, material)
    if validation_map:
        validated = True
        kept = []
        for q in questions_raw:
            v = validation_map.get(q["id"], {})
            status = v.get("status", "ok")
            if status == "drop":
                log.append(f"agent_quiz_maker: dropped question id={q['id']} (not answerable)")
                continue
            if status == "fix" and v.get("fixed_question"):
                q["question"] = v["fixed_question"]
                log.append(f"agent_quiz_maker: fixed question id={q['id']}")
            kept.append(q)
        if len(kept) >= 2:
            questions_raw = kept
            # Re-number ids
            for i, q in enumerate(questions_raw):
                q["id"] = i + 1

    quiz_maker_out: QuizMakerOutput = {
        "quiz_id": quiz_internal.quiz_id,
        "questions": questions_raw,
        "total_questions": len(questions_raw),
        "difficulty": difficulty,
        "topic": quiz_internal.topic,
        "polished": True,
        "validated": validated,
        # Dua arah: request re-extract kalau soal terlalu sedikit
        "requested_reextract": len(questions_raw) < 2,
        "questions_below_minimum": len(questions_raw) < 2,
    }

    # Simpan ke storage agar endpoint submit bisa lookup
    from app.services import quiz_storage
    quiz_storage.save_quiz(quiz_internal)

    # Kirim pesan ke agent lain via agent_messages (komunikasi dua arah)
    messages = list(state.get("agent_messages", []))
    messages.append({
        "from": "quiz_maker",
        "to": "evaluator",
        "msg": f"Quiz dibuat: {len(questions_raw)} soal, difficulty={difficulty}, topic={quiz_internal.topic}",
    })
    if len(questions_raw) < 2:
        messages.append({
            "from": "quiz_maker",
            "to": "extractor",
            "msg": f"Re-extract diperlukan: hanya {len(questions_raw)} soal yang valid",
        })
        log.append("agent_quiz_maker: requesting re-extract from Extractor (soal terlalu sedikit)")

    log.append(
        f"agent_quiz_maker: done — {len(questions_raw)} soal, "
        f"difficulty={difficulty}, validated={validated}"
    )

    return {
        **state,
        "quiz_maker": quiz_maker_out,
        "quiz_id": quiz_internal.quiz_id,
        "agent_log": log,
        "agent_messages": messages,
    }
