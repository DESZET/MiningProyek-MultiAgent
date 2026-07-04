"""Daily Challenge Service.

Manages curated educational materials, deterministically selects a daily material
based on the date, and generates a unique, persistent daily quiz (id format: daily-YYYY-MM-DD)
with special XP rewards.

OWNER: Audry (Backend — Quiz Generator)
"""

from __future__ import annotations

from datetime import date
import hashlib
import logging

from app.schemas.internal import QuizInternal
from app.services import quiz_generator, quiz_storage

logger = logging.getLogger(__name__)

CURATED_MATERIALS = [
    {
        "topic": "Fotosintesis",
        "content": (
            "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
            "dengan bantuan cahaya matahari dan klorofil. Proses vital ini terjadi di "
            "dalam kloroplas sel tumbuhan dan menghasilkan oksigen sebagai produk sampingan. "
            "Reaksi terang berlangsung di membran tilakoid dengan menangkap energi cahaya, "
            "sedangkan reaksi gelap (siklus Calvin) berlangsung di stroma untuk mereduksi "
            "karbondioksida menjadi karbohidrat kompleks yang menjadi sumber energi makhluk hidup."
        )
    },
    {
        "topic": "Siklus Air",
        "content": (
            "Siklus hidrologi atau siklus air menggambarkan pergerakan air yang berkelanjutan "
            "di bumi, atmosfer, dan bawah tanah. Proses evaporasi mengubah air permukaan menjadi uap, "
            "yang kemudian mengalami kondensasi membentuk awan di atmosfer tinggi. "
            "Ketika tetesan air di awan menjadi cukup berat, terjadi presipitasi berupa hujan atau salju. "
            "Air hujan yang jatuh ke daratan akan meresap ke dalam tanah melalui infiltrasi dan mengalir kembali ke laut."
        )
    },
    {
        "topic": "Teori Relativitas",
        "content": (
            "Teori relativitas khusus yang dikemukakan oleh Albert Einstein pada tahun 1905 mengubah "
            "pemahaman kita tentang ruang dan waktu. Teori ini menyatakan bahwa hukum fisika adalah sama "
            "untuk semua pengamat yang bergerak konstan, dan kecepatan cahaya dalam vakum adalah mutlak "
            "tidak peduli kecepatan pengamat. Salah satu konsekuensi paling terkenal dari teori relativitas "
            "ini adalah kesetaraan massa dan energi yang dirumuskan dalam persamaan ikonik E sama dengan m c kuadrat."
        )
    },
    {
        "topic": "Tata Surya",
        "content": (
            "Sistem Tata Surya kita terdiri dari Matahari sebagai pusat gravitasi dan delapan planet "
            "yang mengitarinya dalam orbit elips. Planet dalam seperti Merkurius, Venus, Bumi, dan Mars "
            "sebagian besar terdiri dari batuan padat dan logam. Sementara itu, planet luar yang raksasa "
            "seperti Jupiter, Saturnus, Uranus, dan Neptunus didominasi oleh gas hidrogen, helium, dan es. "
            "Gaya gravitasi matahari yang sangat kuat menjaga semua benda langit tetap berada pada jalurnya."
        )
    },
    {
        "topic": "Candi Borobudur",
        "content": (
            "Candi Borobudur adalah candi Buddha terbesar di dunia yang dibangun pada masa Dinasti Syailendra "
            "sekitar abad ke-9 masehi. Monumen megah ini berbentuk mandala raksasa dengan sembilan platform "
            "bertingkat yang melambangkan kosmologi Buddha. Dinding candi dihiasi dengan ribuan panel relief "
            "bernilai seni tinggi yang menceritakan kisah kehidupan Buddha Gautama dan ajaran dharma. "
            "Struktur Borobudur terdiri dari jutaan blok batu andesit yang dirakit tanpa menggunakan semen."
        )
    }
]


def get_daily_material(today: date) -> dict:
    """Deterministically select one curated material based on the date."""
    date_str = today.strftime("%Y-%m-%d")
    # Use MD5 hash of date string to get a stable, pseudo-random index
    h = hashlib.md5(date_str.encode("utf-8")).hexdigest()
    idx = int(h, 16) % len(CURATED_MATERIALS)
    return CURATED_MATERIALS[idx]


def get_or_create_daily_quiz(today: date, difficulty: str = "medium") -> QuizInternal:
    """Retrieve or generate the daily challenge quiz for the given date.
    The daily quiz ID is formatted as 'daily-YYYY-MM-DD'.
    """
    quiz_id = f"daily-{today.strftime('%Y-%m-%d')}"
    
    # Try retrieving from persistent hybrid store
    existing_quiz = quiz_storage.get_quiz(quiz_id)
    if existing_quiz is not None:
        logger.info("daily_challenge: Daily quiz %s retrieved from store", quiz_id)
        return existing_quiz

    # Otherwise, generate a new one from today's curated material
    material = get_daily_material(today)
    logger.info("daily_challenge: Generating fresh daily quiz %s on topic %s", quiz_id, material["topic"])
    
    quiz = quiz_generator.generate_quiz(
        material_text=material["content"],
        difficulty=difficulty,
        quiz_id=quiz_id,
        topic=material["topic"],  # Use curated topic directly to ensure aggregation
    )
    
    # Save in hybrid storage (memory + DB persistent)
    quiz_storage.save_quiz(quiz)
    return quiz
