"""Integration tests for /quiz/* routes.

These will fail until the underlying services (quiz_generator,
quiz_evaluator, understanding_classifier) are implemented. They serve as
end-to-end smoke tests that validate routing + error handling, not the
business logic itself.

Marked xfail where the service is not yet implemented; remove the marker
when ready.
"""

import pytest

from app.services import quiz_storage


def test_generate_rejects_short_material(client):
    """Short material should return 400 MATERIAL_TOO_SHORT (caught by Pydantic
    or by quiz_generator's defense-in-depth check)."""
    res = client.post(
        "/quiz/generate",
        json={"material_text": "Pendek banget."},
    )
    assert res.status_code in (400, 422)


def test_generate_rejects_empty_material(client):
    """Empty material is caught by Pydantic min_length validation."""
    res = client.post(
        "/quiz/generate",
        json={"material_text": ""},
    )
    assert res.status_code == 422


def test_submit_unknown_quiz_returns_404(client):
    """Submitting against a non-existent quiz_id returns QUIZ_NOT_FOUND."""
    res = client.post(
        "/quiz/submit",
        json={
            "quiz_id": "does-not-exist",
            "answers": [],
            "time_taken_seconds": 0,
        },
    )
    assert res.status_code == 404
    body = res.json()
    assert body["code"] == "QUIZ_NOT_FOUND"


def test_submit_saved_quiz_route(client, sample_quiz):
    quiz_storage.clear_all()
    quiz_storage.save_quiz(sample_quiz)

    answers = [
        {"question_id": q.id, "selected_option_index": q.correct_option_index}
        for q in sample_quiz.questions
    ]
    res = client.post(
        "/quiz/submit",
        json={
            "quiz_id": sample_quiz.quiz_id,
            "answers": answers,
            "time_taken_seconds": 100,
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert body["quiz_id"] == sample_quiz.quiz_id
    assert body["score"]["score_percentage"] == 100
    assert body["score"]["wrong_count"] == 0
    assert body["score"]["unanswered_count"] == 0
    assert body["understanding_level"] in {"high", "medium", "low"}
    assert isinstance(body["insight"], str) and body["insight"]
    assert isinstance(body["recommendation"], str) and body["recommendation"]


@pytest.mark.xfail(reason="quiz_generator not yet implemented (Audry)")
def test_generate_then_submit_full_flow(client):
    """Full happy path. xfail until generator + evaluator + classifier
    are implemented."""
    sample = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. "
        "Reaksi terang berlangsung di tilakoid, sedangkan reaksi gelap "
        "berlangsung di stroma."
    )
    gen = client.post("/quiz/generate", json={"material_text": sample})
    assert gen.status_code == 200
    quiz_id = gen.json()["quiz_id"]
    questions = gen.json()["questions"]

    answers = [
        {"question_id": q["id"], "selected_option_index": 0} for q in questions
    ]
    submit = client.post(
        "/quiz/submit",
        json={
            "quiz_id": quiz_id,
            "answers": answers,
            "time_taken_seconds": 120,
        },
    )
    assert submit.status_code == 200
    body = submit.json()
    assert body["understanding_level"] in {"high", "medium", "low"}
    assert isinstance(body["insight"], str) and body["insight"]
    assert isinstance(body["recommendation"], str) and body["recommendation"]
