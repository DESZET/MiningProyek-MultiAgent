"""Insight engine — generates a 1-2 sentence Indonesian explanation.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

Pure function. Use the templates in BRAND.md §7.6 as the starting point.

Voice rules (BRAND.md §6):
    - Honest: don't pretend the system is more sophisticated than it is
    - Encouraging but not cheesy: no "GREAT JOB!!!", no excessive emoji
    - Calm, focused: library-vibe, not arcade
    - Use "kamu" not "Anda"
"""

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel


def generate_insight(
    level: UnderstandingLevel,
    eval_result: EvaluationResult,
) -> str:
    """Generate a 1-2 sentence insight in Indonesian."""
    score = eval_result.score_percentage
    time = eval_result.time_taken_seconds
    unanswered = eval_result.unanswered_count
    total = eval_result.total_questions

    fast = time <= total * 60
    slow = time > total * 90

    if level == UnderstandingLevel.HIGH:
        if fast:
            return (
                "Skor tinggi dengan waktu pengerjaan efisien menunjukkan kamu menguasai konsep utama materi."
            )
        if slow:
            return (
                "Skor kamu tinggi, tapi waktu pengerjaan cukup lama — mungkin masih ada bagian yang bikin kamu ragu."
            )
        return (
            "Kamu memahami materi dengan baik dan mampu menjawab sebagian besar soal dengan benar."
        )

    if level == UnderstandingLevel.MEDIUM:
        if unanswered > total * 0.3:
            return (
                "Kamu skip beberapa soal — coba lebih percaya diri di pengerjaan berikutnya."
            )
        if slow:
            return (
                "Kamu memahami sebagian materi, tapi waktu pengerjaan menunjukkan kamu masih sering ragu."
            )
        if score >= 65:
            return (
                "Pemahaman kamu cukup solid, tapi masih ada beberapa konsep yang perlu diperkuat."
            )
        return (
            "Kamu memahami sebagian besar materi, tapi ada beberapa konsep yang masih perlu diteguhkan."
        )

    # LOW
    if unanswered > total * 0.5:
        return (
            "Sebagian besar soal tidak kamu jawab — baca ulang materi dulu sebelum mengerjakan kuis lagi."
        )
    if score < 30:
        return (
            "Skor sangat rendah — konsep dasar materi ini perlu kamu pelajari ulang dari awal."
        )
    return (
        "Banyak konsep dasar yang masih perlu dipelajari ulang sebelum kamu lanjut ke materi berikutnya."
    )