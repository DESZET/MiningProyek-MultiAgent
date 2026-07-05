"""Agent Tools — tool functions yang bisa dipanggil Asahi chatbot.

Implementasi AI_AGENT_IDEAS.md §Agent Asahi — tools:
    - get_quiz_history(device_id)   : riwayat kuis pengguna
    - get_weak_topics(device_id)    : topik-topik yang perlu diperkuat
    - generate_new_quiz(topic, ...)  : trigger generate kuis baru dari topik
    - search_study_tips(topic)      : tips belajar dari knowledge base internal

Setiap tool:
    - Punya return schema konsisten (dict)
    - Punya fallback graceful kalau DB tidak tersedia
    - Tidak pernah raise ke caller — selalu return dict dengan "error" key kalau gagal

Pola: thin service — route tidak perlu tahu detail implementasi.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("asahlagi")

# ============================================================================
# Tool: get_quiz_history
# ============================================================================


def get_quiz_history(device_id: str | None, limit: int = 5) -> dict:
    """Ambil riwayat kuis terbaru pengguna.

    Return:
        {
            "success": bool,
            "history": [{"topic", "score", "understanding_level", "completed_at"}, ...],
            "total_quizzes": int,
            "average_score": int,
        }
    """
    if not device_id:
        return {"success": False, "error": "device_id tidak tersedia", "history": []}

    try:
        from app.db.session import is_db_configured
        from app.services import gamification_service

        if not is_db_configured():
            return {"success": False, "error": "database tidak tersedia", "history": []}

        history = gamification_service.get_history(device_id.strip(), limit=limit)
        summary = gamification_service.get_history_summary(device_id.strip())
        return {
            "success": True,
            "history": [
                {
                    "topic": h.get("topic", "Umum"),
                    "score": h.get("score", 0),
                    "understanding_level": h.get("understanding_level", ""),
                    "completed_at": str(h.get("completed_at", "")),
                }
                for h in history
            ],
            "total_quizzes": summary.get("total_quizzes", 0),
            "average_score": summary.get("average_score", 0),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_tools.get_quiz_history failed: %s", exc)
        return {"success": False, "error": str(exc), "history": []}


# ============================================================================
# Tool: get_weak_topics
# ============================================================================


def get_weak_topics(device_id: str | None, limit: int = 3) -> dict:
    """Identifikasi topik lemah pengguna berdasarkan riwayat kuis.

    Return:
        {
            "success": bool,
            "weak_topics": [{"topic": str, "average_score": int, "attempts": int}, ...],
        }
    """
    if not device_id:
        return {"success": False, "error": "device_id tidak tersedia", "weak_topics": []}

    try:
        from app.db.session import is_db_configured
        from app.services import gamification_service

        if not is_db_configured():
            return {"success": False, "error": "database tidak tersedia", "weak_topics": []}

        analytics = gamification_service.get_analytics(device_id.strip())
        topic_mastery = analytics.get("topic_mastery", [])

        # Sort by average_score ascending → topik dengan skor terendah = paling lemah
        weak = sorted(topic_mastery, key=lambda t: t.get("average_score", 100))[:limit]
        return {
            "success": True,
            "weak_topics": [
                {
                    "topic": t.get("topic", "Umum"),
                    "average_score": t.get("average_score", 0),
                    "attempts": t.get("attempt_count", 0),
                }
                for t in weak
            ],
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_tools.get_weak_topics failed: %s", exc)
        return {"success": False, "error": str(exc), "weak_topics": []}


# ============================================================================
# Tool: generate_new_quiz
# ============================================================================


def generate_new_quiz(topic: str, difficulty: str = "medium", num_questions: int = 5) -> dict:
    """Generate kuis baru dari sebuah topik (nama topik jadi material teks).

    Asahi bisa panggil ini ketika user minta "buatkan soal tentang X".
    Karena tidak ada material teks, kita generate contoh kalimat deskriptif
    tentang topik tersebut sebagai seed, lalu lempar ke quiz_generator.

    Return:
        {
            "success": bool,
            "quiz_id": str | None,
            "message": str,
        }
    """
    topic = topic.strip()[:100]
    if not topic:
        return {"success": False, "quiz_id": None, "message": "Topik tidak boleh kosong."}

    # Buat seed material sederhana tentang topik
    seed_material = (
        f"{topic} adalah salah satu topik penting dalam pembelajaran. "
        f"Pemahaman tentang {topic} mencakup konsep dasar, prinsip-prinsip utama, "
        f"dan penerapannya dalam konteks yang relevan. "
        f"Mempelajari {topic} memerlukan pemahaman mendalam tentang definisi, "
        f"karakteristik, dan hubungannya dengan konsep-konsep terkait. "
        f"Penguasaan {topic} dapat membantu dalam memahami berbagai fenomena "
        f"dan menyelesaikan masalah yang berkaitan dengan bidang tersebut."
    )

    try:
        from app.services import quiz_generator

        quiz = quiz_generator.generate_quiz(
            material_text=seed_material,
            difficulty=difficulty,
            topic=topic,
            num_questions=num_questions,
        )
        return {
            "success": True,
            "quiz_id": quiz.quiz_id,
            "message": (
                f"Kuis tentang '{topic}' sudah dibuat dengan {len(quiz.questions)} soal. "
                f"Pergi ke halaman utama untuk mulai kuis, atau beri tahu quiz_id-nya: {quiz.quiz_id}"
            ),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("agent_tools.generate_new_quiz failed: %s", exc)
        return {
            "success": False,
            "quiz_id": None,
            "message": (
                f"Belum bisa generate kuis tentang '{topic}' sekarang. "
                "Coba tempel materinya langsung di halaman utama ya."
            ),
        }


# ============================================================================
# Tool: search_study_tips
# ============================================================================

# Knowledge base internal — tips belajar per kategori topik
_STUDY_TIPS_KB: dict[str, list[str]] = {
    "matematika": [
        "Latihan soal setiap hari lebih efektif daripada belajar sekaligus banyak.",
        "Tulis langkah-langkah penyelesaian secara runtut, jangan loncat-loncat.",
        "Cek kembali jawaban dengan cara berbeda (misalnya substitusi kembali).",
    ],
    "bahasa": [
        "Baca teks asli dalam bahasa target setiap hari, meski singkat.",
        "Catat kata baru dalam konteks kalimat, bukan daftar isolasi.",
        "Praktik menulis pendek (jurnal/cerita) lebih cepat meningkatkan kemampuan.",
    ],
    "sains": [
        "Hubungkan konsep baru dengan fenomena sehari-hari yang sudah kamu kenal.",
        "Gambar diagram atau mind map untuk visualisasi hubungan antar konsep.",
        "Pahami 'mengapa' di balik rumus, bukan hanya hafal rumusnya.",
    ],
    "sejarah": [
        "Buat garis waktu (timeline) untuk membantu mengingat urutan kejadian.",
        "Cari kaitan sebab-akibat antar peristiwa, bukan hafal fakta satu-satu.",
        "Ceritakan ulang apa yang kamu pelajari dengan kata-katamu sendiri.",
    ],
    "default": [
        "Spaced repetition: ulang materi di hari 1, 3, 7, dan 14 setelah belajar.",
        "Pomodoro: 25 menit fokus, 5 menit istirahat — hindari belajar marathon.",
        "Ajarkan materi ke orang lain (atau ke diri sendiri) untuk cek pemahaman.",
        "Tidur cukup setelah belajar — konsolidasi memori terjadi saat tidur.",
    ],
}


def search_study_tips(topic: str) -> dict:
    """Cari tips belajar yang relevan dari knowledge base internal.

    Return:
        {
            "success": bool,
            "topic": str,
            "tips": [str, ...],
        }
    """
    topic_lower = topic.lower().strip()

    matched_key = "default"
    for key in _STUDY_TIPS_KB:
        if key in topic_lower or topic_lower in key:
            matched_key = key
            break

    tips = _STUDY_TIPS_KB.get(matched_key, _STUDY_TIPS_KB["default"])
    return {
        "success": True,
        "topic": topic,
        "category": matched_key,
        "tips": tips,
    }
