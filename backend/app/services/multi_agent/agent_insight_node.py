"""Agent Insight — node LangGraph untuk generate insight, rekomendasi, dan study path.

AI_AGENT_IDEAS.md §Agent Insight + §Study Path Generator:
    - Input: EvaluatorOutput dari Agent Evaluator
    - Generate insight personal pakai LLM (bukan template statis)
    - Generate study path: urutan topik yang perlu dipelajari
    - Output: InsightOutput di AgentState

Study Path Generator:
    - "Kamu perlu kuasai A dulu sebelum B."
    - Baca history + generate urutan topik dari weak_topics & strong_topics
"""

from __future__ import annotations

import logging
import os

import httpx

from app.services.multi_agent.state import AgentState, InsightOutput

logger = logging.getLogger("asahlagi.insight")

_API_URL = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"
_TIMEOUT_S = 25.0

_SYSTEM_PROMPT = """\
Kamu adalah sistem analisis belajar "Asahlagi" yang memberikan insight personal \
dan jalur belajar kepada pengguna berdasarkan hasil kuis mereka.

OUTPUT FORMAT — tulis persis 4 bagian dipisahkan "---":

BAGIAN 1 (Insight):
1-2 kalimat spesifik tentang performa. Sebutkan skor, topik kuat/lemah. \
Jangan generik. Gunakan "kamu".

---

BAGIAN 2 (Rekomendasi):
1-2 kalimat aksi konkret. Kalau level medium/low, akhiri dengan "asah lagi".

---

BAGIAN 3 (Study Path):
Daftar 3-5 topik dalam urutan yang disarankan, satu per baris. \
Format: "1. [topik] — [alasan singkat]"

---

BAGIAN 4 (Adaptive Difficulty):
Satu kata saja: easy / medium / hard

ATURAN KETAT:
- JANGAN markdown (tanpa **, #). Kalimat biasa.
- JANGAN mengarang angka di luar data yang diberikan.
- Output HARUS persis 4 bagian dengan pemisah "---"."""


def _parse_llm_output(text: str) -> tuple[str, str, list[str], str] | None:
    """Parse 4-bagian output. Return (insight, recommendation, study_path, difficulty)."""
    parts = [p.strip() for p in text.split("---") if p.strip()]
    if len(parts) < 4:
        return None

    insight = parts[0].strip()
    recommendation = parts[1].strip()

    # Parse study path (numbered list)
    study_path = []
    for line in parts[2].splitlines():
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            # Strip numbering/bullets
            clean = line.lstrip("0123456789.-) ").strip()
            if clean:
                study_path.append(clean)

    diff_raw = parts[3].strip().lower()
    difficulty = diff_raw if diff_raw in {"easy", "medium", "hard"} else "medium"

    return insight, recommendation, study_path, difficulty


def _call_llm(evaluator: dict) -> tuple[str, str, list[str], str] | None:
    """Panggil LLM untuk insight + study path. Return None kalau gagal."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None

    score = evaluator.get("score_percentage", 0)
    correct = evaluator.get("correct_count", 0)
    wrong = evaluator.get("wrong_count", 0)
    unanswered = evaluator.get("unanswered_count", 0)
    total = evaluator.get("total_questions", 0)
    time_s = evaluator.get("time_taken_seconds", 0)
    level = evaluator.get("understanding_level", "low")
    weak = evaluator.get("weak_topics", [])
    strong = evaluator.get("strong_topics", [])
    adaptive = evaluator.get("adaptive_difficulty", "medium")

    prompt = (
        f"DATA HASIL KUIS:\n"
        f"- Skor: {score}%\n"
        f"- Benar: {correct}, Salah: {wrong}, Tidak dijawab: {unanswered} dari {total} soal\n"
        f"- Waktu: {time_s} detik\n"
        f"- Level pemahaman: {level}\n"
        f"- Topik lemah: {', '.join(weak) if weak else 'tidak terdeteksi'}\n"
        f"- Topik kuat: {', '.join(strong) if strong else 'tidak terdeteksi'}\n"
        f"- Rekomendasi difficulty berikutnya: {adaptive}\n\n"
        "Buat insight, rekomendasi, study path, dan konfirmasi difficulty sesuai format."
    )

    try:
        resp = httpx.post(
            _API_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.6,
                "max_tokens": 400,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
        return _parse_llm_output(text)
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_insight_node: LLM failed: %s", exc)
        return None


def run(state: AgentState) -> AgentState:
    """LangGraph node: generate insight + study path dari EvaluatorOutput."""
    log = list(state.get("agent_log", []))
    log.append("agent_insight: start")

    evaluator = state.get("evaluator")
    if not evaluator:
        state["error"] = "Evaluator belum berjalan."
        state["agent_log"] = log
        return state

    # Coba LLM
    result = _call_llm(evaluator)

    if result:
        insight, recommendation, study_path, adaptive_difficulty = result
        log.append("agent_insight: LLM insight+study_path generated")
    else:
        # Fallback ke rule-based
        log.append("agent_insight: using rule-based fallback")
        from app.services import insight_engine, recommendation_engine
        from app.schemas.result import UnderstandingLevel

        # Reconstruct eval_result dari state untuk rule-based
        eval_result = state.get("_eval_result")  # type: ignore[typeddict-item]
        level_str = evaluator.get("understanding_level", "low")
        level = UnderstandingLevel(level_str)

        if eval_result:
            insight = insight_engine.generate_insight(level, eval_result)
            recommendation = recommendation_engine.generate_recommendation(level, eval_result)
        else:
            insight = "Hasil kuis sudah direkam."
            recommendation = "Lanjutkan belajar dan asah lagi."

        # Fallback study path dari weak_topics
        weak = evaluator.get("weak_topics", [])
        study_path = [f"{t} — perlu dipelajari ulang" for t in weak[:3]]
        adaptive_difficulty = evaluator.get("adaptive_difficulty", "medium")

    insight_out: InsightOutput = {
        "insight": insight,
        "recommendation": recommendation,
        "study_path": study_path,
        "adaptive_difficulty": adaptive_difficulty,
    }

    log.append(
        f"agent_insight: done — study_path={len(study_path)} items, "
        f"adaptive_difficulty={adaptive_difficulty}"
    )

    return {**state, "insight": insight_out, "agent_log": log}
