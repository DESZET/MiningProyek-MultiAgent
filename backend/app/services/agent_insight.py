"""Agent Insight — LLM-powered insight & recommendation generator.

Upgrade dari insight_engine.py dan recommendation_engine.py yang masih rule-based.
Sekarang pakai GPT-4o-mini untuk generate insight & rekomendasi yang personal.

Arsitektur (AI_AGENT_IDEAS.md §Fase 1):
    - Input: EvaluationResult + UnderstandingLevel
    - LLM generate insight personal (bukan template statis)
    - Fallback ke rule-based (insight_engine.py) kalau LLM tidak tersedia

Pola: thin-wrapper — logic di sini, bukan di route.
"""

from __future__ import annotations

import logging
import os

import httpx

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel
from app.services import insight_engine, recommendation_engine

logger = logging.getLogger("asahlagi")

_API_URL = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"
_TIMEOUT_S = 20.0

_LEVEL_LABEL = {"high": "tinggi", "medium": "sedang", "low": "rendah"}

_SYSTEM_PROMPT = """\
Kamu adalah sistem analisis hasil kuis pembelajaran bahasa Indonesia bernama "Asahlagi".
Tugasmu: baca data hasil kuis pengguna lalu tulis satu insight dan satu rekomendasi.

ATURAN WAJIB:
- Bahasa Indonesia santai tapi informatif. Gunakan "kamu".
- Insight: 1-2 kalimat. Spesifik terhadap data (skor, waktu, topik lemah). Jangan generik.
- Rekomendasi: 1-2 kalimat. Aksi konkret yang bisa dilakukan pengguna. Akhiri rekomendasi \
level medium/low dengan kata "asah lagi".
- JANGAN mengarang angka atau fakta di luar data yang diberikan.
- JANGAN markdown (tanpa **, #, atau list). Tulis kalimat biasa.
- Output HARUS persis dua paragraf, dipisahkan baris kosong:
  Paragraf 1 = insight
  Paragraf 2 = rekomendasi"""


def _build_prompt(level: UnderstandingLevel, eval_result: EvaluationResult) -> str:
    score = eval_result.score_percentage
    correct = eval_result.correct_count
    wrong = eval_result.wrong_count
    unanswered = eval_result.unanswered_count
    total = eval_result.total_questions
    time_s = eval_result.time_taken_seconds
    avg_time = eval_result.average_time_per_question
    level_str = _LEVEL_LABEL.get(level.value, level.value)

    # Ambil topik lemah kalau tersedia (dari question_results via tipe soal yang salah)
    wrong_indices = [
        r.question_id for r in eval_result.question_results if not r.is_correct
    ]

    return (
        f"DATA HASIL KUIS:\n"
        f"- Skor: {score}%\n"
        f"- Benar: {correct}, Salah: {wrong}, Tidak dijawab: {unanswered} dari {total} soal\n"
        f"- Waktu total: {time_s} detik (rata-rata {avg_time:.1f} detik/soal)\n"
        f"- Level pemahaman: {level_str}\n"
        f"- Nomor soal yang salah: {wrong_indices if wrong_indices else 'tidak ada'}\n\n"
        "Tulis insight dan rekomendasi sesuai format dua paragraf yang diminta."
    )


def _call_llm(prompt: str) -> tuple[str, str] | None:
    """Panggil LLM, parse dua paragraf. Return None kalau gagal/token tidak ada."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None
    try:
        resp = httpx.post(
            _API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.6,
                "max_tokens": 200,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_insight: LLM call failed (%s), using rule-based fallback", exc)
        return None

    # Parse dua paragraf
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) >= 2:
        return paragraphs[0], paragraphs[1]

    # Fallback: split di newline tunggal
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) >= 2:
        mid = len(lines) // 2
        return " ".join(lines[:mid]), " ".join(lines[mid:])

    if lines:
        return lines[0], lines[0]

    return None


def generate_insight_and_recommendation(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> tuple[str, str]:
    """Generate (insight, recommendation) via LLM, fallback ke rule-based.

    Return tuple (insight, recommendation) — selalu berhasil karena ada fallback.
    """
    prompt = _build_prompt(level, eval_result)
    result = _call_llm(prompt)

    if result is not None:
        insight, recommendation = result
        logger.info("agent_insight: LLM insight generated successfully")
        return insight, recommendation

    # Fallback rule-based
    logger.info("agent_insight: using rule-based fallback")
    return (
        insight_engine.generate_insight(level, eval_result),
        recommendation_engine.generate_recommendation(level, eval_result),
    )
