"""FastAPI application entry point.

Wires up:
    - CORS middleware (per API.md §9)
    - Global exception handlers for ApiException + unhandled exceptions
    - Routers from app/routes/

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
import traceback

from dotenv import load_dotenv

# Load .env before any module reads os.getenv (e.g. ml.generator reads HF_SPACE_URL at import).
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.routes import auth, chat, gamification, health, quiz
from app.routes.gamification import GAMIFICATION_UNAVAILABLE
from app.utils.errors import ApiException, AUTH_UNAVAILABLE, INTERNAL_ERROR
from app.utils.limiter import limiter


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173", "http://localhost:3000"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("asahlagi")


app = FastAPI(
    title="Asahlagi API",
    description="Asah lagi sampai paham. — capstone TP-G005 backend.",
    version=__version__,
)

app.state.limiter = limiter

# CORS — per API.md §9
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_origins(os.getenv("CORS_ALLOWED_ORIGINS")),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    # X-Device-Id is required by gamification endpoints; without it the browser
    # preflight blocks those requests (curl works because it skips preflight).
    allow_headers=["Content-Type", "X-Device-Id"],
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ============================================================================
# Exception handlers — per API.md §2 (response envelope + global error policy)
# ============================================================================


@app.exception_handler(ApiException)
async def api_exception_handler(_: Request, exc: ApiException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.exception_handler(OperationalError)
async def db_unavailable_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """A configured-but-unreachable database (Neon scaled to zero, network down,
    wrong host) must degrade to a 503 contract — never a 500 — so the optional
    DB-backed surfaces stay optional and the core quiz UX keeps working.

    Scoped to the optional surfaces only (/gamification/*, /auth/*). A DB failure
    on any other endpoint keeps its standard 500 semantics instead of being
    mislabeled as a degraded-feature outage.
    """
    path = request.url.path
    if path.startswith("/gamification"):
        detail, code = "Fitur progres sedang tidak tersedia. Coba lagi sebentar.", GAMIFICATION_UNAVAILABLE
    elif path.startswith("/auth"):
        detail, code = "Login sedang tidak tersedia. Coba lagi sebentar.", AUTH_UNAVAILABLE
    else:
        return await unhandled_exception_handler(request, exc)
    logger.warning("Database unavailable on %s, serving 503: %s", path, exc)
    return JSONResponse(status_code=503, content={"detail": detail, "code": code})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ada hambatan dari sisi kami. Coba lagi sebentar.",
            "code": INTERNAL_ERROR,
        },
    )


# ============================================================================
# Routers
# ============================================================================

app.include_router(health.router)
app.include_router(quiz.router)
app.include_router(gamification.router)
app.include_router(auth.router)
app.include_router(chat.router)
