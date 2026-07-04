"""Asahlagi Quiz Generator — Hugging Face Space (FastAPI + IndoT5).

Hosted at: https://<username>-asahlagi-quizgen.hf.space

Endpoints:
    GET  /            — health check
    POST /generate    — generate quiz from material text

The local backend (backend/app/services/quiz_generator.py) calls this Space.
If unreachable, backend falls back to local CPU inference, then rule-based.

Quiz assembly (answer-span selection, question consistency, cloze fallback,
same-category distractors) lives in `qg_core.py`, a verbatim copy of
`backend/ml/generator/qg_core.py`. The Space and the local backend share that
file so both serve identical answer-aware quizzes. Keep the two copies in sync.
"""

from __future__ import annotations

import logging
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import qg_core

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Config
# ============================================================================

MODEL_NAME = "raviarnan/indot5-quizgen-asahlagi"  # fine-tuned on TyDiQA-id (was Wikidepia/IndoT5-base)
MAX_INPUT_LENGTH = 512
MAX_OUTPUT_LENGTH = 48
NUM_BEAMS = 4
REPETITION_PENALTY = 1.8
NO_REPEAT_NGRAM_SIZE = 3
NUM_QUESTIONS = 5


# ============================================================================
# Lifespan: load model once at startup
# ============================================================================

_tokenizer = None
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup, before any request comes in."""
    global _tokenizer, _model
    from transformers import T5ForConditionalGeneration, T5Tokenizer

    logger.info("Loading IndoT5 from HF Hub: %s", MODEL_NAME)
    _tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    _model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    _model.eval()
    logger.info(
        "Model loaded (%dM params)",
        sum(p.numel() for p in _model.parameters()) // 1_000_000,
    )
    yield
    # On shutdown — nothing to clean up
    logger.info("Shutting down")


app = FastAPI(
    title="Asahlagi Quiz Generator (HF Space)",
    description="Indonesian question generator using fine-tuned IndoT5",
    version="0.2.0",
    lifespan=lifespan,
)


# ============================================================================
# Models
# ============================================================================


class GenerateRequest(BaseModel):
    material_text: str = Field(..., min_length=100, max_length=20_000)
    # §4.3 Quiz settings — requested question count (backend clamps to 3/5/7/10).
    num_questions: int = Field(default=NUM_QUESTIONS, ge=1, le=10)


class GeneratedQuestion(BaseModel):
    question: str
    options: list[str]
    correct_option_index: int


class GenerateResponse(BaseModel):
    questions: list[GeneratedQuestion]


# ============================================================================
# Model call — raw decode; all cleaning/validation lives in qg_core
# ============================================================================


def _run_model(prompt: str) -> str:
    """Run IndoT5 on an answer-aware prompt; return raw decoded text.

    qg_core.build_quiz passes the highlighted (`<hl>`) prompt and handles all
    cleaning, consistency checking, and cloze fallback on the result.
    """
    if _model is None or _tokenizer is None:
        raise RuntimeError("Model not loaded")

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
    )
    outputs = _model.generate(
        **inputs,
        max_length=MAX_OUTPUT_LENGTH,
        num_beams=NUM_BEAMS,
        repetition_penalty=REPETITION_PENALTY,
        no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,
        early_stopping=True,
    )
    return _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


# ============================================================================
# Routes
# ============================================================================


@app.get("/")
async def root():
    return {
        "service": "asahlagi-quizgen",
        "model": MODEL_NAME,
        "status": "ready" if _model is not None else "loading",
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if _model is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not yet loaded")

    text = req.material_text.strip()

    # Deterministic per-material RNG so the same text yields a stable quiz
    # (mirrors backend/ml/generator/inference.py).
    rng = random.Random(abs(hash(text)) & 0xFFFFFFFF)
    questions = qg_core.build_quiz(
        text, _run_model, num_questions=req.num_questions, rng=rng
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Material too short or homogeneous to build a quiz",
        )

    return GenerateResponse(
        questions=[GeneratedQuestion(**q) for q in questions]
    )
