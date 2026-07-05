"""Agent Extractor — node LangGraph untuk ekstrak & analisis materi.

AI_AGENT_IDEAS.md §Agent Extractor:
    - Input: URL, PDF bytes, atau teks mentah
    - Tugas: ekstrak teks, deteksi bahasa, bersihkan noise, nilai kualitas
    - Improvement: tambah LLM summarize kalau materi > 3000 karakter
    - Output: ExtractorOutput di AgentState

Dipanggil oleh orchestrator sebagai node pertama di "generate" flow.
"""

from __future__ import annotations

import logging
import os
import re

import httpx

from app.services.multi_agent.state import AgentState, ExtractorOutput

logger = logging.getLogger("asahlagi.extractor")

_API_URL = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"
_TIMEOUT_S = 20.0
_SUMMARIZE_THRESHOLD = 3000   # karakter — materi lebih panjang akan di-summarize

_ID_MARKERS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "adalah", "dengan", "pada",
    "ini", "itu", "tidak", "akan", "dalam", "karena", "jika", "serta",
}
_EN_MARKERS = {
    "the", "is", "are", "was", "were", "this", "that", "with", "from",
    "have", "has", "been", "they", "their", "which", "when", "where",
}


def _detect_language(text: str) -> str:
    words = set(re.findall(r"[a-z]+", text.lower()))
    id_score = len(words & _ID_MARKERS)
    en_score = len(words & _EN_MARKERS)
    if id_score >= 3:
        return "id"
    if en_score >= 3:
        return "en"
    return "unknown"


def _count_sentences(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if len(s.split()) >= 3])


def _estimate_topic(text: str) -> str:
    """Ambil kalimat pertama sebagai perkiraan topik (max 80 karakter)."""
    first = re.split(r"[.!?\n]", text.strip())[0].strip()
    return first[:80] if first else "Umum"


def _summarize_with_llm(text: str) -> str | None:
    """Rangkum teks panjang jadi ~1500 karakter pakai LLM. Return None kalau gagal."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None
    try:
        resp = httpx.post(
            _API_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Kamu adalah asisten yang merangkum teks pendidikan bahasa Indonesia. "
                            "Tugas: rangkum teks berikut menjadi 3-5 paragraf padat (sekitar 1000-1500 karakter). "
                            "Pertahankan semua konsep kunci, definisi, dan fakta penting. "
                            "Gunakan bahasa Indonesia yang jelas. Jangan tambahkan opini atau analisis."
                        ),
                    },
                    {"role": "user", "content": f"Rangkum teks ini:\n\n{text[:6000]}"},
                ],
                "temperature": 0.3,
                "max_tokens": 600,
            },
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        summary = (resp.json()["choices"][0]["message"]["content"] or "").strip()
        return summary if len(summary) >= 200 else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_extractor: summarize failed: %s", exc)
        return None


def run(state: AgentState) -> AgentState:
    """LangGraph node: proses raw_input menjadi clean_text + metadata.

    Untuk input bertipe 'url' dan 'pdf', delegasikan ke source_extractor
    yang sudah ada. Untuk 'text', langsung bersihkan.
    Tambahkan LLM summarize untuk materi yang sangat panjang.
    """
    log = list(state.get("agent_log", []))
    log.append("agent_extractor: start")

    raw = state.get("raw_input") or ""
    input_type = state.get("input_type", "text")

    # Ekstrak teks berdasarkan tipe input
    clean_text = ""
    try:
        if input_type == "url":
            from app.services.source_extractor import extract_text_from_url
            clean_text = extract_text_from_url(raw)
        elif input_type == "pdf":
            # raw_input berisi bytes encoded sebagai latin-1 string (dari route)
            from app.services.source_extractor import extract_text_from_pdf
            pdf_bytes = raw.encode("latin-1") if isinstance(raw, str) else raw
            clean_text = extract_text_from_pdf(pdf_bytes)
        else:
            clean_text = raw.strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_extractor: extraction failed: %s", exc)
        state["error"] = f"Gagal mengekstrak materi: {exc}"
        state["agent_log"] = log
        return state

    # Quality check
    from app.services.material_quality import assess
    quality_ok, quality_hint = assess(clean_text)

    # LLM Summarize kalau teks terlalu panjang
    is_summarized = False
    if quality_ok and len(clean_text) > _SUMMARIZE_THRESHOLD:
        summary = _summarize_with_llm(clean_text)
        if summary:
            clean_text = summary
            is_summarized = True
            log.append(f"agent_extractor: summarized {len(raw)}->{len(clean_text)} chars")

    extractor_out: ExtractorOutput = {
        "clean_text": clean_text,
        "language": _detect_language(clean_text),
        "estimated_topic": _estimate_topic(clean_text),
        "sentence_count": _count_sentences(clean_text),
        "char_count": len(clean_text),
        "is_summarized": is_summarized,
        "quality_ok": quality_ok,
        "quality_hint": quality_hint,
    }

    log.append(
        f"agent_extractor: done — lang={extractor_out['language']}, "
        f"chars={extractor_out['char_count']}, quality={quality_ok}"
    )

    return {**state, "extractor": extractor_out, "agent_log": log}
