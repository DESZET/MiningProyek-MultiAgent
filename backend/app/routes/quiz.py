"""Quiz endpoints — text, URL, and PDF inputs.

Routes are intentionally thin (per ARCHITECTURE.md §5.2). They:
    - parse the request (Pydantic validation or multipart for PDF)
    - call extractor + generator services
    - shape the response

NO business logic lives here. NO try/except for generic exceptions —
the global exception handler in main.py catches ApiException and
unhandled exceptions.
"""

from datetime import date
from fastapi import APIRouter, File, UploadFile, Header, Request

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
    quiz_generator,
    quiz_storage,
    source_extractor,
    submit_coordinator,
    gamification_service,
    daily_challenge,
)
from app.utils.limiter import limiter
from app.utils.errors import ApiException, MATERIAL_TOO_LONG, QUIZ_NOT_FOUND

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Hard limit on PDF file size — prevent abuse / OOM
MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


def _determine_adaptive_difficulty(
    x_device_id: str | None,
    requested_difficulty: str | None,
) -> str:
    """Determine difficulty: use explicit requested if provided.
    Otherwise, if device_id is provided and DB is configured, use user's level.
    Fallback to 'medium'.
    """
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
        except Exception:
            # Fallback gracefully on DB error
            pass

    return "medium"


def _quiz_internal_to_response(quiz_internal) -> QuizGenerateResponse:
    """Strip correct_option_index for client transport."""
    return QuizGenerateResponse(
        quiz_id=quiz_internal.quiz_id,
        questions=[q.to_public() for q in quiz_internal.questions],
        total_questions=quiz_internal.total_questions,
        generated_at=quiz_internal.generated_at,
        difficulty=quiz_internal.difficulty,
    )


# ============================================================================
# Text input — original endpoint
# ============================================================================


@router.post("/generate", response_model=QuizGenerateResponse)
@limiter.limit("3/minute")
def generate_quiz_endpoint(
    request: Request,
    req: QuizGenerateRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/generate — see API.md §4.2."""
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty)
    quiz_internal = quiz_generator.generate_quiz(
        req.material_text,
        difficulty=difficulty,
        num_questions=req.num_questions,
        shuffle_options=req.shuffle_options,
    )
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# URL input — extract article, then generate
# ============================================================================


@router.post("/generate-from-url", response_model=QuizGenerateResponse)
@limiter.limit("3/minute")
def generate_from_url_endpoint(
    request: Request,
    req: QuizGenerateFromUrlRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/generate-from-url — fetch article from URL, generate quiz.

    See API.md §4.4.
    """
    material_text = source_extractor.extract_text_from_url(req.url)
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty)
    quiz_internal = quiz_generator.generate_quiz(
        material_text,
        difficulty=difficulty,
        num_questions=req.num_questions,
        shuffle_options=req.shuffle_options,
    )
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# PDF input — extract text, then generate
# ============================================================================


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
    """POST /quiz/generate-from-pdf — multipart PDF upload, generate quiz.

    See API.md §4.5.
    """
    # Read with size cap to avoid memory blowup on huge files
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_LONG,
            detail=f"File PDF terlalu besar. Maksimal {MAX_PDF_BYTES // (1024 * 1024)} MB.",
        )

    material_text = source_extractor.extract_text_from_pdf(pdf_bytes)
    diff = _determine_adaptive_difficulty(x_device_id, difficulty)
    quiz_internal = quiz_generator.generate_quiz(
        material_text,
        difficulty=diff,
        num_questions=num_questions,
        shuffle_options=shuffle_options,
    )
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# Regenerate — produces a fresh quiz from the same source material as a
# previously generated quiz_id. Powers the "Asah Lagi" button on ResultPage.
# ============================================================================


@router.post("/regenerate", response_model=QuizGenerateResponse)
def regenerate_quiz_endpoint(
    req: QuizRegenerateRequest,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """POST /quiz/regenerate — regenerate a quiz from a prior quiz_id's source."""
    previous = quiz_storage.get_quiz(req.quiz_id)
    if previous is None or not previous.source_material:
        raise ApiException(
            status_code=404,
            code=QUIZ_NOT_FOUND,
            detail="Materi sumber tidak ditemukan. Mulai ulang dari halaman utama.",
        )
    difficulty = _determine_adaptive_difficulty(x_device_id, req.difficulty or previous.difficulty)
    quiz_internal = quiz_generator.generate_quiz(
        previous.source_material,
        difficulty=difficulty,
        quiz_id=req.quiz_id,
    )
    quiz_storage.save_quiz(quiz_internal)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# Daily Challenge — special persistent locked daily quiz
# ============================================================================


@router.get("/daily-challenge", response_model=QuizGenerateResponse)
def get_daily_challenge_endpoint(
    difficulty: str | None = None,
    x_device_id: str | None = Header(default=None),
) -> QuizGenerateResponse:
    """GET /quiz/daily-challenge — get today's daily challenge quiz."""
    diff = _determine_adaptive_difficulty(x_device_id, difficulty)
    today_date = date.today()
    quiz_internal = daily_challenge.get_or_create_daily_quiz(today_date, difficulty=diff)
    return _quiz_internal_to_response(quiz_internal)


# ============================================================================
# Submit (no input-type variation — same flow for all)
# ============================================================================


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz_endpoint(req: QuizSubmitRequest) -> QuizSubmitResponse:
    """POST /quiz/submit — see API.md §4.3."""
    return submit_coordinator.process_submission(
        quiz_id=req.quiz_id,
        answers=req.answers,
        time_taken_seconds=req.time_taken_seconds,
    )

