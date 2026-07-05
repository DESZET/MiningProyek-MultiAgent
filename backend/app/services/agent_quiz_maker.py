"""Agent Quiz Maker — LLM polish step setelah IndoT5 generate soal.

Implementasi AI_AGENT_IDEAS.md §Agent Quiz Maker (Fase 2):
    - Tahap 1: IndoT5 generate soal kasar (sudah ada di quiz_generator.py)
    - Tahap 2 (baru): LLM polish soal — perbaiki grammar, pastikan distractor masuk akal
    - Tahap 3 (baru): LLM validasi — apakah soal terjawab dari materi?

Entry point utama: polish_questions(questions, source_material) → list[QuestionInternal]

Fallback: kalau LLM tidak tersedia atau timeout, kembalikan soal apa adanya.
Pola: thin service — dipanggil dari quiz_generator.py sebagai post-processing step.
"""

from __future__ import annotations

import json
import logging
import os

import httpx

from app.schemas.internal import QuestionInternal

logger = logging.getLogger("asahlagi")

_API_URL = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"
_TIMEOUT_S = 25.0

# Maksimal soal yang di-polish sekaligus (hemat token)
_MAX_POLISH_BATCH = 5

_POLISH_SYSTEM_PROMPT = """\
Kamu adalah editor soal kuis bahasa Indonesia. Tugasmu memperbaiki kualitas soal pilihan ganda.

TUGAS PER SOAL:
1. Perbaiki grammar dan ejaan (EYD/PUEBI) tanpa mengubah makna.
2. Pastikan pertanyaan jelas dan tidak ambigu.
3. Pastikan semua pilihan jawaban (distractor) masuk akal dan tidak terlalu mudah ditebak.
4. Pastikan jawaban benar (correct_option_index) memang benar berdasarkan materi.
5. Kalau soal sudah bagus, kembalikan apa adanya.

OUTPUT FORMAT (JSON array, satu objek per soal):
[
  {
    "id": <integer, sama dengan input>,
    "question": "<teks soal yang sudah diperbaiki>",
    "options": ["<opsi A>", "<opsi B>", "<opsi C>", "<opsi D>"],
    "correct_option_index": <integer 0-3>
  },
  ...
]

ATURAN KETAT:
- Output HANYA JSON array. Tanpa penjelasan, tanpa markdown, tanpa komentar.
- Jangan tambah atau kurangi soal.
- Jangan ubah correct_option_index kecuali kamu yakin 100% itu salah.
- Kalau soal tipe bukan multiple_choice, kembalikan dengan field yang sama tapi tanpa options/correct_option_index."""


def _build_polish_prompt(
    questions: list[QuestionInternal], source_material: str
) -> str:
    material_preview = source_material[:800].strip()
    items = []
    for q in questions:
        item: dict = {"id": q.id, "type": q.type, "question": q.question}
        if q.options:
            item["options"] = q.options
            item["correct_option_index"] = q.correct_option_index
        items.append(item)

    return (
        f"MATERI SUMBER (ringkasan):\n{material_preview}\n\n"
        f"SOAL YANG PERLU DIPERBAIKI:\n{json.dumps(items, ensure_ascii=False, indent=2)}\n\n"
        "Perbaiki soal-soal di atas sesuai instruksi sistem. Output JSON array saja."
    )


def _call_polish(prompt: str) -> list[dict] | None:
    """Panggil LLM untuk polish. Return list dict atau None kalau gagal."""
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
                    {"role": "system", "content": _POLISH_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 1200,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()

        # Strip markdown code fences kalau ada
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()

        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("agent_quiz_maker: JSON parse failed: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_quiz_maker: LLM call failed: %s", exc)
        return None


def _apply_polish(
    original: list[QuestionInternal],
    polished_data: list[dict],
) -> list[QuestionInternal]:
    """Merge hasil polish ke soal original. Kalau data tidak valid, pakai original."""
    polished_by_id = {item.get("id"): item for item in polished_data if isinstance(item, dict)}

    result = []
    for q in original:
        p = polished_by_id.get(q.id)
        if p is None:
            result.append(q)
            continue

        # Hanya update field yang relevan dan valid
        new_question = str(p.get("question", q.question)).strip() or q.question
        new_options = p.get("options")
        new_correct = p.get("correct_option_index")

        # Validasi options
        if (
            q.options
            and isinstance(new_options, list)
            and len(new_options) == len(q.options)
            and all(isinstance(o, str) for o in new_options)
        ):
            validated_options = [str(o).strip() for o in new_options]
        else:
            validated_options = q.options

        # Validasi correct_option_index
        if (
            validated_options
            and isinstance(new_correct, int)
            and 0 <= new_correct < len(validated_options)
        ):
            validated_correct = new_correct
        else:
            validated_correct = q.correct_option_index

        result.append(
            QuestionInternal(
                id=q.id,
                type=q.type,
                question=new_question,
                options=validated_options,
                correct_option_index=validated_correct,
                correct_answer_text=q.correct_answer_text,
                left_items=q.left_items,
                right_items=q.right_items,
                correct_matches=q.correct_matches,
            )
        )
    return result


def polish_questions(
    questions: list[QuestionInternal],
    source_material: str,
) -> list[QuestionInternal]:
    """Polish soal multiple_choice dengan LLM. Non-MC soal dikembalikan apa adanya.

    Fallback graceful: kalau LLM tidak tersedia, kembalikan soal original tanpa perubahan.
    """
    # Pisahkan MC dan non-MC
    mc_questions = [q for q in questions if q.type == "multiple_choice"]
    non_mc = [q for q in questions if q.type != "multiple_choice"]

    if not mc_questions:
        return questions

    # Batasi batch untuk hemat token
    to_polish = mc_questions[:_MAX_POLISH_BATCH]
    skip = mc_questions[_MAX_POLISH_BATCH:]

    prompt = _build_polish_prompt(to_polish, source_material)
    polished_data = _call_polish(prompt)

    if polished_data is None:
        logger.info("agent_quiz_maker: polish skipped (LLM unavailable), using original questions")
        return questions

    polished_mc = _apply_polish(to_polish, polished_data) + skip

    # Gabungkan kembali, pertahankan urutan id original
    all_by_id = {q.id: q for q in polished_mc + non_mc}
    result = [all_by_id.get(q.id, q) for q in questions]

    logger.info("agent_quiz_maker: polished %d/%d questions", len(to_polish), len(mc_questions))
    return result
