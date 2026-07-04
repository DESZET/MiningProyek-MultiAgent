"""Recommendation engine — generates an actionable next step in Indonesian.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function. Use the templates in BRAND.md §7.7 as starting points.

Brand mechanic note (BRAND.md §6 + §7.7):
    The medium and low recommendations end with "asah lagi" — the brand
    name as a callback to the next user action. Preserve this when
    extending templates.
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel


def generate_recommendation(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    """Generate a 1-2 sentence Indonesian recommendation."""
    score = eval_result.score_percentage
    time = eval_result.time_taken_seconds
    unanswered = eval_result.unanswered_count
    total = eval_result.total_questions

    fast = time <= total * 60
    slow = time > total * 90

    if level == UnderstandingLevel.HIGH:
        if fast and score == 100:
            return (
                "Kamu siap untuk materi berikutnya. Coba topik lanjutan atau kuis dengan tingkat kesulitan lebih tinggi."
            )
        if slow:
            return (
                "Lanjut ke materi berikutnya, tapi luangkan waktu untuk review bagian yang membuatmu ragu tadi."
            )
        return (
            "Lanjut ke materi berikutnya, atau coba kuis dengan tingkat kesulitan lebih tinggi."
        )

    if level == UnderstandingLevel.MEDIUM:
        if unanswered > total * 0.3:
            return (
                "Coba alokasikan waktu lebih untuk setiap soal — jangan skip kalau ragu, ambil tebakan terbaik. Lalu asah lagi."
            )
        if slow:
            return (
                "Bagian yang membuatmu ragu kemungkinan jadi penyebab waktu lama. Tinjau ulang konsep itu dulu, lalu asah lagi."
            )
        if score >= 65:
            return (
                "Fokus pada konsep yang masih kurang, lalu asah lagi untuk memastikan pemahamanmu solid."
            )
        return (
            "Tinjau ulang bagian yang masih ragu, lalu asah lagi dalam 1-2 hari."
        )

    # LOW
    if unanswered > total * 0.5:
        return (
            "Baca dan pahami materi dari awal sebelum mengerjakan kuis. Setelah itu asah lagi sambil cek pemahamanmu."
        )
    if score < 30:
        return (
            "Mulai dari poin dasar materi ini — baca pelan-pelan, catat yang penting, lalu asah lagi."
        )
    return (
        "Baca ulang materi dari awal, fokus pada poin dasar, lalu asah lagi."
    )