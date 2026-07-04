import pytest
from app.services import quiz_generator
from app.schemas.internal import QuizInternal, QuestionInternal
from app.utils.errors import ApiException

def test_too_short_raises():
    with pytest.raises(ApiException) as exc:
        quiz_generator.generate_quiz("Pendek banget.")
    assert exc.value.code == "MATERIAL_TOO_SHORT"

def test_normal_material_returns_quiz(monkeypatch):
    # Ensure we use the fallback logic to test it without needing HF space
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 2
    for q in quiz.questions:
        if q.options is None:
            # short_answer (free-text) carries the answer in correct_answer_text.
            assert q.correct_answer_text is not None, f"Q{q.id}: free-text needs answer"
        else:
            # multiple_choice = 4 options, true_false = 2.
            assert len(q.options) in (2, 4), f"Q{q.id}: unexpected option count"
            assert 0 <= q.correct_option_index < len(q.options)

def test_questions_have_unique_ids(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    ids = [q.id for q in quiz.questions]
    assert len(ids) == len(set(ids)), "Question IDs must be unique"

def test_options_are_distinct(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    for q in quiz.questions:
        if q.options is None:
            continue  # short_answer (free-text) has no options
        # Options must be distinct, whatever the count (4 for MC, 2 for T/F).
        assert len(set(q.options)) == len(q.options), f"Q{q.id}: duplicate options"

def test_fallback_on_dl_failure(monkeypatch):
    """Even if DL model unavailable, generator should fall back to rule-based."""
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)

    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    quiz = quiz_generator.generate_quiz(material)
    assert isinstance(quiz, QuizInternal)
    assert len(quiz.questions) >= 2

def test_is_duplicate():
    """Test the deduplication logic directly."""
    existing = [
        QuestionInternal(id=1, question="Apa itu fotosintesis?", options=["A", "B", "C", "D"], correct_option_index=0)
    ]
    
    # Highly similar (should be true)
    assert quiz_generator._is_duplicate("Apakah itu fotosintesis?", existing) is True
    
    # Not similar (should be false)
    assert quiz_generator._is_duplicate("Dimana proses reaksi gelap terjadi?", existing) is False


def test_adaptive_difficulty_easy(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    # Easy should target 3 questions
    quiz = quiz_generator.generate_quiz(material, difficulty="easy")
    assert isinstance(quiz, QuizInternal)
    assert quiz.difficulty == "easy"
    assert len(quiz.questions) == 3


def test_adaptive_difficulty_hard(monkeypatch):
    from ml.generator import inference
    monkeypatch.setattr(inference, "is_available", lambda: False)
    
    material = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan bantuan cahaya matahari dan klorofil. "
        "Proses vital ini berlangsung di kloroplas sel tumbuhan dan menghasilkan oksigen sebagai produk sampingan. "
        "Reaksi terang berlangsung di membran tilakoid dengan menangkap energi cahaya matahari secara langsung. "
        "Sementara itu, reaksi gelap atau siklus Calvin berlangsung di stroma tanpa memerlukan bantuan cahaya. "
        "Tumbuhan menyerap air dari dalam tanah melalui akar dan mendistribusikannya ke seluruh bagian daun. "
        "Karbondioksida diserap dari udara bebas melalui stomata yang terletak di permukaan bawah daun. "
        "Glukosa yang dihasilkan digunakan oleh tumbuhan sebagai sumber energi utama untuk pertumbuhan mereka. "
        "Kelebihan glukosa akan disimpan dalam bentuk pati di berbagai organ tumbuhan seperti buah atau umbi."
    )
    # Hard should target 7 questions
    quiz = quiz_generator.generate_quiz(material, difficulty="hard")
    assert isinstance(quiz, QuizInternal)
    assert quiz.difficulty == "hard"
    assert len(quiz.questions) >= 4


def test_daily_challenge():
    from app.services import daily_challenge
    from datetime import date
    today = date(2026, 5, 26)
    
    material = daily_challenge.get_daily_material(today)
    assert "topic" in material
    assert len(material["content"]) >= 100
    
    # Check deterministic choice
    assert daily_challenge.get_daily_material(today) == material


def test_quiz_storage_hybrid():
    from app.services import quiz_storage
    from app.schemas.internal import QuizInternal, QuestionInternal
    from datetime import datetime, timezone
    
    q = QuizInternal(
        quiz_id="test-hybrid-id",
        questions=[
            QuestionInternal(id=1, question="Q1?", options=["A", "B", "C", "D"], correct_option_index=0)
        ],
        generated_at=datetime.now(timezone.utc),
        source_material="Test source material text here for verification.",
        difficulty="easy"
    )
    
    quiz_storage.save_quiz(q)
    retrieved = quiz_storage.get_quiz("test-hybrid-id")
    assert retrieved is not None
    assert retrieved.quiz_id == "test-hybrid-id"
    assert retrieved.difficulty == "easy"
    assert retrieved.source_material == "Test source material text here for verification."

