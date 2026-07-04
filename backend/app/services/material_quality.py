"""Lightweight 'quizability' pre-check (ROADMAP §3.2).

The quiz generator is built for Indonesian learning prose. This flags clearly
unsuitable material early (CVs, English text, bare lists) so users get a helpful
hint instead of a nonsensical quiz — before waiting ~15s for generation.

Deliberately conservative: only blocks material that is clearly a poor fit, so
ordinary Indonesian study text always passes.
"""

from __future__ import annotations

import re

# High-frequency Indonesian function words — dense in real prose, ~absent in
# English text or CV/keyword dumps. A low density is a strong "not Indonesian
# prose" signal.
_ID_FUNCTION_WORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "adalah", "dengan", "pada",
    "ini", "itu", "atau", "tidak", "akan", "dalam", "sebagai", "oleh", "juga",
    "karena", "jika", "agar", "supaya", "bisa", "dapat", "merupakan", "yaitu",
    "serta", "namun", "tetapi", "sehingga", "maka", "para", "setiap", "ketika",
    "sebuah", "seorang", "lebih", "saat", "secara", "antara", "tersebut",
}

# The generator already enforces a 100-char floor, so this only guards against
# the rare very-short-but-not-empty case; keep it low to avoid false positives.
_MIN_WORDS = 20
_MIN_ID_RATIO = 0.04
_MIN_SENTENCES = 2

_STRUCTURAL_NOISE_CHARS = '|↑↓→←↳·•►▪'
# Threshold: reject only when >5% of characters are structural noise.
# This avoids false-rejecting valid educational text that contains a few bullets
# or table pipes (e.g. Wikipedia paste, bulleted notes).
_NOISE_RATIO_THRESHOLD = 0.05

_BRAND_LIKE_RE = re.compile(r"^[a-z]+[A-Z][a-zA-Z]*$|^[A-Z]{2,}[a-z]+$")
# Brand-ratio threshold loosened to 0.25 to avoid false-rejecting texts with
# legitimate acronyms (e.g. UNESCO, ASEAN, HTTP, CPU).
_BRAND_RATIO_THRESHOLD = 0.25


def assess(text: str) -> tuple[bool, str | None]:
    """Return (is_suitable, hint). `hint` is a user-facing reason when unsuitable."""

    # 1. Structural noise check — ratio-based, not any-occurrence.
    #    A single bullet • or pipe | no longer rejects the entire material.
    if len(text) > 0:
        noise_count = sum(1 for c in text if c in _STRUCTURAL_NOISE_CHARS)
        if noise_count / len(text) > _NOISE_RATIO_THRESHOLD:
            return False, (
                "Materi mengandung banyak simbol atau elemen format (seperti tabel/daftar). "
                "Sistem butuh teks paragraf yang bersih agar bisa membuat kuis yang baik."
            )

    # 2. Alpha ratio check — denominator excludes whitespace/newlines so that
    #    normal prose with numbers/dates isn't falsely rejected.
    non_ws_chars = [c for c in text if not c.isspace()]
    if non_ws_chars:
        alpha_count = sum(1 for c in non_ws_chars if c.isalpha())
        if alpha_count / len(non_ws_chars) < 0.55:
            return False, (
                "Materi terlalu banyak mengandung angka, simbol, atau tanda baca. "
                "Coba gunakan materi yang lebih didominasi oleh teks/kalimat."
            )

    # 3. Brand-like token density — loosened threshold
    words_raw = text.split()
    if words_raw:
        brand_count = sum(1 for w in words_raw if _BRAND_LIKE_RE.match("".join(c for c in w if c.isalpha())))
        if brand_count / len(words_raw) > _BRAND_RATIO_THRESHOLD:
            return False, (
                "Materi ini terlalu banyak mengandung nama merek atau istilah non-standar. "
                "Gunakan materi penjelasan edukasional yang umum."
            )

    # 4. Word count check
    words = re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())
    n = len(words)
    if n < _MIN_WORDS:
        return False, (
            "Materinya terlalu pendek untuk kuis yang baik. Tambahkan penjelasan "
            "lebih lengkap — minimal beberapa kalimat/paragraf."
        )

    # 5. Indonesian prose density
    id_ratio = sum(1 for w in words if w in _ID_FUNCTION_WORDS) / n
    if id_ratio < _MIN_ID_RATIO:
        return False, (
            "Materi ini sepertinya bukan teks belajar berbahasa Indonesia (mis. CV, "
            "daftar poin, atau berbahasa Inggris), jadi kuisnya kurang akurat. Coba "
            "tempel materi berupa paragraf penjelasan dalam Bahasa Indonesia."
        )

    # 6. Sentence count
    sentences = [s for s in re.split(r"[.!?]+", text) if len(s.split()) >= 4]
    if len(sentences) < _MIN_SENTENCES:
        return False, (
            "Materi ini kurang berupa kalimat penjelasan (lebih mirip daftar/poin). "
            "Coba tempel materi berupa paragraf agar kuisnya lebih relevan."
        )

    return True, None
