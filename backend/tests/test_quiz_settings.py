"""§4.3 Quiz settings (pre-generate): num_questions + shuffle_options.

Exercises the service through the rule-based path (is_available=False) so the
tests are deterministic and don't need the DL model.
"""

import pytest

from app.services import quiz_generator
from app.schemas.internal import QuizInternal


# A material with many distinct sentences so the generator can reach 10 questions.
_LONG_MATERIAL = (
    "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
    "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
    "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi terang "
    "berlangsung di tilakoid dan mengubah energi cahaya menjadi energi kimia. "
    "Reaksi gelap berlangsung di stroma dan dikenal sebagai siklus Calvin. "
    "Air diserap oleh akar tumbuhan dari dalam tanah melalui rambut akar. "
    "Karbon dioksida masuk melalui stomata yang berada pada permukaan daun. "
    "Klorofil memberikan warna hijau pada daun tumbuhan tingkat tinggi. "
    "Glukosa hasil fotosintesis disimpan dalam bentuk amilum di dalam umbi. "
    "Mitokondria adalah organel tempat berlangsungnya respirasi seluler. "
    "Respirasi menghasilkan energi dalam bentuk molekul adenosina trifosfat. "
    "Membran sel mengatur keluar masuknya zat dari dan ke dalam sitoplasma. "
    "Inti sel menyimpan materi genetik berupa kromosom yang membawa sifat."
)


@pytest.fixture(autouse=True)
def _force_rule_based(monkeypatch):
    """Force the rule-based path so tests are deterministic (no DL model)."""
    from ml.generator import inference

    monkeypatch.setattr(inference, "is_available", lambda: False)


def test_num_questions_caps_count_at_3():
    quiz = quiz_generator.generate_quiz(_LONG_MATERIAL, num_questions=3)
    assert isinstance(quiz, QuizInternal)
    assert 2 <= len(quiz.questions) <= 3


def test_num_questions_10_yields_more_than_default():
    quiz = quiz_generator.generate_quiz(_LONG_MATERIAL, num_questions=10)
    assert len(quiz.questions) <= 10
    # The long material has >10 usable sentences, so asking for 10 should beat
    # the default-of-5 ceiling.
    assert len(quiz.questions) > 5


def test_num_questions_overrides_difficulty_count():
    # 'easy' alone would target 3; an explicit num_questions must win.
    quiz = quiz_generator.generate_quiz(
        _LONG_MATERIAL, difficulty="easy", num_questions=7
    )
    assert len(quiz.questions) > 3


def test_num_questions_none_falls_back_to_difficulty():
    easy = quiz_generator.generate_quiz(_LONG_MATERIAL, difficulty="easy")
    assert len(easy.questions) <= 3


def test_num_questions_clamped_to_max_10():
    # Out-of-range values must not explode; service clamps to <= 10.
    quiz = quiz_generator.generate_quiz(_LONG_MATERIAL, num_questions=99)
    assert len(quiz.questions) <= 10


def test_shuffle_off_sorts_mc_options():
    quiz = quiz_generator.generate_quiz(
        _LONG_MATERIAL, num_questions=10, shuffle_options=False
    )
    for q in quiz.questions:
        if q.type == "multiple_choice" and q.options:
            assert q.options == sorted(q.options), (
                f"Q{q.id}: options must be in stable sorted order when shuffle is off"
            )
            # The correct index must still point at the right option.
            assert 0 <= q.correct_option_index < len(q.options)


def test_shuffle_off_preserves_correct_answer():
    """Reordering options must not break which answer is correct."""
    shuffled = quiz_generator.generate_quiz(
        _LONG_MATERIAL, num_questions=10, shuffle_options=True
    )
    fixed = quiz_generator.generate_quiz(
        _LONG_MATERIAL, num_questions=10, shuffle_options=False
    )
    # Same material → same questions; the correct option *text* must match even
    # though its position differs.
    by_id_shuffled = {q.id: q for q in shuffled.questions}
    for q in fixed.questions:
        if q.type != "multiple_choice" or not q.options:
            continue
        other = by_id_shuffled.get(q.id)
        if other is None or not other.options:
            continue
        assert (
            q.options[q.correct_option_index]
            == other.options[other.correct_option_index]
        )


def test_true_false_options_not_reordered_by_shuffle_off():
    """Benar/Salah ordering is semantic — must stay [Benar, Salah]."""
    quiz = quiz_generator.generate_quiz(
        _LONG_MATERIAL, num_questions=10, shuffle_options=False
    )
    for q in quiz.questions:
        if q.type == "true_false" and q.options:
            assert q.options == ["Benar", "Salah"]
