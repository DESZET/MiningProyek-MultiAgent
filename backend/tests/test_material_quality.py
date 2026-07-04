"""Tests for the quizability pre-check (ROADMAP §3.2)."""

from app.services.material_quality import assess

_INDONESIAN_PROSE = (
    "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan "
    "bantuan cahaya matahari dan klorofil. Proses ini terjadi di kloroplas dan "
    "menghasilkan oksigen sebagai produk samping. Reaksi terang berlangsung di "
    "tilakoid, sedangkan reaksi gelap berlangsung di stroma."
)


def test_indonesian_prose_is_suitable():
    ok, hint = assess(_INDONESIAN_PROSE)
    assert ok is True
    assert hint is None


def test_english_text_is_flagged():
    text = (
        "Aprilia is a software engineer who developed scalable systems and led the "
        "engineering department. She worked collaboratively and improved production "
        "environments. Her skills include leadership and time management."
    )
    ok, hint = assess(text)
    assert ok is False
    assert hint and "Indonesia" in hint


def test_too_short_is_flagged():
    ok, hint = assess("Halo, ini materi yang sangat singkat saja ya.")
    assert ok is False
    assert hint is not None
