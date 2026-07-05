"""Quiz endpoints — text, URL, and PDF inputs.

Routes are intentionally thin (per ARCHITECTURE.md §5.2). They:
    - parse the request (Pydantic validation or multipart for PDF)
    - call orchestrator (multi-agent) or legacy services
    - shape the response

Multi-Agent upgrade (AI_AGENT_IDEAS.md §Fase 3):
    - /quiz/generate, /quiz/generate-from-url, /quiz/generate-from-pdf →
      jalankan lewat multi_agent.orchestrator.run_generate_flow()
    - /quiz/submit → lewat run_submit_flow() dengan feedback loop Evaluator→Insight
    - /quiz/submit response kini menyertakan study_path dan retry_quiz_id
    - /quiz/feedback → real-time feedback Asahi per soal (§Real-time Feedback)

NO business logic lives here. NO try/except for generic exceptions —
the global exception handler in main.py catches ApiException and
unhandled exceptions.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Header, Request, UploadFile
from pydantic import BaseModel

from app.db.session import is_db_configured
from app.schemas.quiz import (
    QuizGenerateFromUrlRequest,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizRegenerateRequest,
    QuizSubmitRequest,
)
from app.schemas.result import QuizSubmitResponse
from app.services import (
    daily_challenge,
    gamification_service,
    quiz_generator,
    quiz_storage,
    source_extractor,
    submit_coordinator,
)
from app.services.multi_agent import orchestrator
from app.utils.errors import ApiException, MATERIAL_LOW_QUALITY, MATERIAL_TOO_LONG, QUIZ_NOT_FOUND
from app.utils.limiter import limiter

router = APIRouter(prefix="/quiz", tags=["quiz"])

MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


# ============================================================================
# Extended response schemas (multi-agent additions)
# ============================================================================


class QuizSubmitExtendedResponse(QuizSubmitResponse):
    """Extend QuizSubmitResponse dengan field multi-agent tambahan."""
    study_path: list[str] = []          # Study Path Generator output
    retry_quiz_id: Optional[str] = None # Auto-Retry Question: quiz_id baru kalau needs_retry
    agent_log: list[str] = []           # Audit trail agent yang berjalan


class QuizFeedbackRequest(BaseModel):
    """POST /quiz/feedback — real-time feedback per soal saat kuis berlangsung."""
    quiz_id: str
    question_id: int
    selected_option_index: Optional[int] = None
    is_answered: bool = True


class QuizFeedbackResponse(BaseModel):
    """Response real-time feedback dari Asahi per soal."""
    hint: str               # Komentar singkat Asahi tentang soal ini
    is_correct: Optional[bool] = None  # None kalau belum dikonfirmasi


# ============================================================================
# Helpers
# ============================================================================


def _determine_adaptive_difficulty(
    x_device_id: str | None,
    requested_difficulty: str | None,
) -> str:
    if requested_difficulty:
        return requested_difficulty
    if x_device_id and x_device_id.strip() and is_db_configured():
        try:
            stats = gamification_service.get_stats(x_device_id.strip())
            level = stats.get("level", 1)
            if level <= 3:
                return "easy"
            elif level <= 8:
                return "medium"
            else:
                return "hard"
        except Exception:  # noqa: BLE001
            pass
    return "medium"


def _quiz_internal_to_response(quiz_internal) -> QuizGenerateResponse:
    return QuizGenerateResponse(
        quiz_id=quiz_internal.quiz_id,
        questions=[q.to_public() for q in quiz_internal.questions],
        total_questions=quiz_internal.total_questions,
        generated_at=quiz_internal.generated_at,
        difficulty=quiz_internal.difficulty,
    )


def _state_to_generate_response(state: dict) -> QuizGenerateResponse:
    """Convert orchestrator final state ke QuizGenerateResponse."""
    if state.get("error"):
        raise ApiException(
            status_code=400,
            code=MATERIAL_LOW_QUALITY,
            detail=state["error"],
        )
    quiz_maker = state.get("quiz_maker")
    if not quiz_maker:
        raise ApiException(
            status_code=500,
            code="QUIZ_GENERATION_FAILED",
            detail="Gagal generate kuis. Coba lagi sebentar.",
        )
    # Quiz sudah disimpan ke storage oleh agent_quiz_maker_node
    quiz_id = quiz_maker["quiz_id"]
    quiz = quiz_storage.get_quiz(quiz_id)
    if quiz is None:
        raise ApiException(
            status_code=500,
            code="QUIZ_GENERATION_FAILED",
            detail="Gagal menyimpan kuis. Coba lagi.",
        )
    return _quiz_internal_to_response(quiz)


# ============================================================================
# Generate endpoints — lewat Multi-Agent Orchestrator
# ============================================================================


@router.post("/generate", response_model=QuizGenerateResponse)
@limiter.limit("3/minute")
def generate_quiz_endpoint(
    request: Request,
    req: QuizGenerateRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/generate — diproses lewat multi-agent orchestrator.

    Flow: Agent Extractor → Agent Quiz Maker (dengan LLM polish + validasi).
    """
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty)
    state = orchestrator.run_generate_flow(
        raw_input=req.material_text,
        input_type="text",
        difficulty=difficulty,
        num_questions=req.num_questions or 5,
        shuffle_options=req.shuffle_options,
        device_id=x_device_id,
    )
    return _state_to_generate_response(state)


@router.post("/generate-from-url", response_model=QuizGenerateResponse)
@limiter.limit("3/minute")
def generate_from_url_endpoint(
    request: Request,
    req: QuizGenerateFromUrlRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/generate-from-url — Agent Extractor handles URL fetching."""
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty)
    state = orchestrator.run_generate_flow(
        raw_input=req.url,
        input_type="url",
        difficulty=difficulty,
        num_questions=req.num_questions or 5,
        shuffle_options=req.shuffle_options,
        device_id=x_device_id,
    )
    return _state_to_generate_response(state)


@router.post("/generate-from-pdf", response_model=QuizGenerateResponse)
@limiter.limit("3/minute")
async def generate_from_pdf_endpoint(
    request: Request,
    file: UploadFile = File(...),
    difficulty: str | None = None,
    num_questions: int | None = None,
    shuffle_options: bool = True,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/generate-from-pdf — Agent Extractor handles PDF parsing."""
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_LONG,
            detail=f"File PDF terlalu besar. Maksimal {MAX_PDF_BYTES // (1024 * 1024)} MB.",
        )
    diff = _determine_adaptive_difficulty(x_device_id, difficulty)
    # Encode bytes ke latin-1 string agar bisa masuk ke state (akan di-decode agent)
    raw_input = pdf_bytes.decode("latin-1")
    state = orchestrator.run_generate_flow(
        raw_input=raw_input,
        input_type="pdf",
        difficulty=diff,
        num_questions=num_questions or 5,
        shuffle_options=shuffle_options,
        device_id=x_device_id,
    )
    return _state_to_generate_response(state)


# ============================================================================
# Regenerate — tetap pakai legacy path (source material sudah ada di storage)
# ============================================================================


@router.post("/regenerate", response_model=QuizGenerateResponse)
def regenerate_quiz_endpoint(
    req: QuizRegenerateRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/regenerate — regenerate dari source material yang sama."""
    previous = quiz_storage.get_quiz(req.quiz_id)
    if previous is None or not previous.source_material:
        raise ApiException(
            status_code=404,
            code=QUIZ_NOT_FOUND,
            detail="Materi sumber tidak ditemukan. Mulai ulang dari halaman utama.",
        )
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty or previous.difficulty)
    # Jalankan lewat orchestrator dengan source material yang sudah ada
    state = orchestrator.run_generate_flow(
        raw_input=previous.source_material,
        input_type="text",
        difficulty=difficulty,
        num_questions=previous.total_questions,
        shuffle_options=True,
        device_id=x_device_id,
    )
    return _state_to_generate_response(state)


# ============================================================================
# Daily Challenge
# ============================================================================


@router.get("/daily-challenge", response_model=QuizGenerateResponse)
def get_daily_challenge_endpoint(
    difficulty: str | None = None,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """GET /quiz/daily-challenge — tetap pakai legacy path (daily quiz khusus)."""
    diff = _determine_adaptive_difficulty(x_device_id, difficulty)
    today_date = date.today()
    quiz_internal = daily_challenge.get_or_create_daily_quiz(today_date, difficulty=diff)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# Submit — lewat Multi-Agent Orchestrator dengan feedback loop
# ============================================================================


@router.post("/submit", response_model=QuizSubmitExtendedResponse)
def submit_quiz_endpoint(
    req: QuizSubmitRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizSubmitExtendedResponse:
    """POST /quiz/submit — diproses lewat multi-agent orchestrator.

    Flow: Agent Evaluator → {needs_retry → Agent Quiz Maker | Agent Insight}

    Response menyertakan:
    - study_path: jalur belajar yang disarankan (Study Path Generator)
    - retry_quiz_id: quiz baru kalau skor < 50 (Auto-Retry Question)
    - agent_log: audit trail agent yang berjalan
    """
    answers_raw = [a.model_dump() for a in req.answers]

    state = orchestrator.run_submit_flow(
        quiz_id=req.quiz_id,
        answers=answers_raw,
        time_taken_seconds=req.time_taken_seconds,
        device_id=x_device_id,
    )

    if state.get("error") and not state.get("evaluator"):
        raise ApiException(
            status_code=404,
            code=QUIZ_NOT_FOUND,
            detail=state["error"],
        )

    # Ambil hasil dari state agents (bisa None kalau LLM timeout)
    evaluator = state.get("evaluator") or {}
    insight = state.get("insight") or {}
    quiz_maker = state.get("quiz_maker")  # berisi retry quiz kalau needs_retry

    # Gunakan submit_coordinator legacy untuk build QuizSubmitResponse base
    # (untuk backward compat dengan gamification recording)
    base_response = submit_coordinator.process_submission(
        quiz_id=req.quiz_id,
        answers=req.answers,
        time_taken_seconds=req.time_taken_seconds,
    )

    # Override insight & recommendation dengan hasil agent (lebih kaya)
    final_insight = insight.get("insight") or base_response.insight
    final_recommendation = insight.get("recommendation") or base_response.recommendation

    return QuizSubmitExtendedResponse(
        quiz_id=base_response.quiz_id,
        score=base_response.score,
        time_taken_seconds=base_response.time_taken_seconds,
        understanding_level=base_response.understanding_level,
        insight=final_insight,
        recommendation=final_recommendation,
        chart_data=base_response.chart_data,
        submitted_at=base_response.submitted_at,
        question_reviews=base_response.question_reviews,
        # Multi-agent extras
        study_path=insight.get("study_path", []),
        retry_quiz_id=quiz_maker.get("quiz_id") if quiz_maker and evaluator.get("needs_retry") else None,
        agent_log=state.get("agent_log", []),
    )


# ============================================================================
# Real-time Feedback per soal (AI_AGENT_IDEAS.md §Real-time Feedback Saat Kuis)
# ============================================================================


@router.post("/feedback", response_model=QuizFeedbackResponse)
def quiz_feedback_endpoint(req: QuizFeedbackRequest) -> QuizFeedbackResponse:
    """POST /quiz/feedback — Asahi beri komentar singkat di tengah kuis.

    AI_AGENT_IDEAS.md §Real-time Feedback:
    'Asahi bisa komentar di tengah kuis (bukan hanya di akhir).
    Butuh Agent Asahi yang bisa dipanggil per-soal.'

    Dipanggil frontend setelah user menjawab satu soal.
    Tidak ada evaluasi penuh — hanya hint motivasi singkat dari Asahi.
    """
    import os
    import httpx

    quiz = quiz_storage.get_quiz(req.quiz_id)
    if quiz is None:
        return QuizFeedbackResponse(hint="Terus semangat!", is_correct=None)

    questions_by_id = {q.id: q for q in quiz.questions}
    q = questions_by_id.get(req.question_id)
    if q is None:
        return QuizFeedbackResponse(hint="Lanjut ke soal berikutnya!", is_correct=None)

    is_correct: bool | None = None
    if req.is_answered and req.selected_option_index is not None:
        is_correct = req.selected_option_index == q.correct_option_index

    # Generate hint singkat dari Asahi
    token = os.getenv("GITHUB_TOKEN")
    hint = _default_hint(is_correct, req.question_id, len(quiz.questions))
    if token:
        try:
            resp = httpx.post(
                "https://models.github.ai/inference/chat/completions",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Kamu adalah 'Asahi', teman belajar di Asahlagi. "
                                "Beri komentar SANGAT SINGKAT (1 kalimat, max 15 kata) tentang jawaban user. "
                                "Tone: hangat, kalem, tidak lebay. Bahasa Indonesia kasual. Tanpa emoji berlebihan."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Soal {req.question_id} dari {len(quiz.questions)}. "
                                f"Status: {'benar' if is_correct else 'salah' if is_correct is False else 'belum dijawab'}. "
                                "Beri komentar singkat."
                            ),
                        },
                    ],
                    "temperature": 0.8,
                    "max_tokens": 40,
                },
                timeout=8.0,
            )
            resp.raise_for_status()
            llm_hint = (resp.json()["choices"][0]["message"]["content"] or "").strip()
            if llm_hint:
                hint = llm_hint
        except Exception:  # noqa: BLE001
            pass  # gunakan default hint

    return QuizFeedbackResponse(hint=hint, is_correct=is_correct)


def _default_hint(is_correct: bool | None, question_id: int, total: int) -> str:
    remaining = total - question_id
    if is_correct is True:
        return "Tepat! Lanjut terus."
    elif is_correct is False:
        if remaining > 0:
            return f"Masih ada {remaining} soal, tetap fokus ya."
        return "Hampir selesai, tetap semangat!"
    return "Yuk lanjut ke soal berikutnya!"
