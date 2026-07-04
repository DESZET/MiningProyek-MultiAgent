"""Inference for the quiz generator (DL — IndoT5).

Inference strategy (in order of preference):
    1. HF Space (cloud) via HTTP — set HF_SPACE_URL env var
    2. Local CPU via transformers — auto-loads if HF Space unreachable
    3. Caller (app/services/quiz_generator.py) falls back to rule-based

This 3-tier approach gives demo resilience: if HF Space sleeps or
internet is down, local CPU still works; if local model isn't installed,
rule-based still works.

OWNER: Audry (integration + quality), Ravi (HF Space setup)
"""

from __future__ import annotations

import logging
import os
import random
import re
import time
import difflib
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIG
# ============================================================================

# DECISION (2026-05-08): use base pretrained IndoT5 without fine-tuning.
# See ML.md §3 for rationale (fp16 NaN issue with T5 fine-tuning).

_LOCAL_MODEL_NAME = "Wikidepia/IndoT5-base"

# HF Space endpoint (cloud inference). Set via env var:
#   export HF_SPACE_URL="https://<username>-asahlagi-quizgen.hf.space"
# If unset or unreachable, falls back to local CPU inference.
_HF_SPACE_URL = os.getenv("HF_SPACE_URL", "").rstrip("/")
_HF_SPACE_TIMEOUT_SECONDS = 60.0
_HF_SPACE_HEALTH_TIMEOUT_SECONDS = 15.0
# Re-probe a previously-unreachable Space after this many seconds. Free Spaces
# sleep after 48h idle and take ~30-60s to wake, so the first probe after a
# sleep can fail; without re-probing the backend would serve rule-based for the
# whole process life instead of recovering once the Space is awake.
_HF_SPACE_RECHECK_COOLDOWN_SECONDS = 30.0

# Generation hyperparameters (used only by local fallback)
_MAX_INPUT_LENGTH = 512
_MAX_OUTPUT_LENGTH = 48
_NUM_BEAMS = 4
_REPETITION_PENALTY = 1.8
_NO_REPEAT_NGRAM_SIZE = 3
_NUM_QUESTIONS = 5

# ============================================================================
# Module-level state for LOCAL inference (loaded lazily)
# ============================================================================

_local_tokenizer = None
_local_model = None
_local_load_attempted = False
_local_load_error: Optional[str] = None


def _load_local_model() -> None:
    """Try to load local model. Called lazily — only if HF Space is unavailable."""
    global _local_tokenizer, _local_model, _local_load_attempted, _local_load_error
    if _local_load_attempted:
        return
    _local_load_attempted = True
    try:
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        logger.info("ml.generator: Loading local IndoT5 from %s ...", _LOCAL_MODEL_NAME)
        _local_tokenizer = T5Tokenizer.from_pretrained(_LOCAL_MODEL_NAME)
        _local_model = T5ForConditionalGeneration.from_pretrained(_LOCAL_MODEL_NAME)
        _local_model.eval()
        logger.info(
            "ml.generator: Loaded local IndoT5 (params=%dM)",
            sum(p.numel() for p in _local_model.parameters()) // 1_000_000,
        )
    except Exception as exc:  # noqa: BLE001
        _local_load_error = f"{type(exc).__name__}: {exc}"
        logger.warning(
            "ml.generator: Failed to load local model (%s) — only HF Space + rule-based fallback available",
            _local_load_error,
        )


# ============================================================================
# HF Space client
# ============================================================================

_hf_space_available_cached: Optional[bool] = None
_hf_space_last_negative_check: float = 0.0


def _check_hf_space_available() -> bool:
    """Health check on HF Space.

    A positive result is cached for the process lifetime (the Space is up). A
    negative result is NOT sticky: free Spaces sleep after 48h idle and take
    ~30-60s to wake, so the first probe after a sleep can fail. We re-probe
    after a short cooldown instead of permanently dropping to rule-based — a
    sleeping Space at startup would otherwise silently disable cloud inference
    for the entire process (e.g. through a whole demo)."""
    global _hf_space_available_cached, _hf_space_last_negative_check
    if _hf_space_available_cached:
        return True
    if not _HF_SPACE_URL:
        return False
    # Recently probed and failed — don't hammer it (or block every request on a
    # timeout) until the cooldown elapses.
    if (
        _hf_space_available_cached is False
        and (time.monotonic() - _hf_space_last_negative_check)
        < _HF_SPACE_RECHECK_COOLDOWN_SECONDS
    ):
        return False
    try:
        import httpx

        with httpx.Client(timeout=_HF_SPACE_HEALTH_TIMEOUT_SECONDS) as client:
            response = client.get(f"{_HF_SPACE_URL}/")
            if response.status_code == 200 and response.json().get("status") == "ready":
                logger.info("ml.generator: HF Space available at %s", _HF_SPACE_URL)
                _hf_space_available_cached = True
                return True
            logger.warning(
                "ml.generator: HF Space at %s returned status=%d (re-probe in %.0fs)",
                _HF_SPACE_URL,
                response.status_code,
                _HF_SPACE_RECHECK_COOLDOWN_SECONDS,
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "ml.generator: HF Space unreachable (%s) — re-probe in %.0fs",
            exc,
            _HF_SPACE_RECHECK_COOLDOWN_SECONDS,
        )
    _hf_space_available_cached = False
    _hf_space_last_negative_check = time.monotonic()
    return False


def _generate_via_hf_space(material_text: str, num_questions: int) -> list[dict]:
    """Call HF Space /generate endpoint. Returns list of question dicts."""
    import httpx

    with httpx.Client(timeout=_HF_SPACE_TIMEOUT_SECONDS) as client:
        response = client.post(
            f"{_HF_SPACE_URL}/generate",
            json={"material_text": material_text, "num_questions": num_questions},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("questions", [])


# ============================================================================
# Public API
# ============================================================================


def is_available() -> bool:
    """Return True if EITHER HF Space OR local model is loadable."""
    if _check_hf_space_available():
        return True
    _load_local_model()
    return _local_model is not None


def generate(material_text: str, num_questions: int | None = None) -> list[dict]:
    """Generate quiz from material. Tries HF Space, falls back to local CPU.

    `num_questions` (§4.3) is the requested question count; defaults to
    _NUM_QUESTIONS. Threaded to both the HF Space request and local inference.

    Returns: list of dicts with keys {question, options, correct_option_index}
    Raises: RuntimeError if both HF Space and local model unavailable.
    """
    n = num_questions if num_questions is not None else _NUM_QUESTIONS
    # Path 1: HF Space (cloud)
    if _check_hf_space_available():
        try:
            questions = _generate_via_hf_space(material_text, n)
            if questions:
                logger.info(
                    "ml.generator: HF Space produced %d questions",
                    len(questions),
                )
                return questions
            logger.warning("ml.generator: HF Space returned empty list, trying local")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ml.generator: HF Space request failed (%s), trying local",
                exc,
            )

    # Path 2: local CPU
    _load_local_model()
    if _local_model is None:
        raise RuntimeError(
            f"ml.generator unavailable: HF Space + local both failed. "
            f"Local error: {_local_load_error}"
        )
    return _generate_locally(material_text, n)


# ============================================================================
# Local inference logic (fallback path) — shares the answer-aware core
# ============================================================================

from ml.generator import qg_core


def _run_local_model(prompt: str) -> str:
    """Run the local IndoT5 on a prompt; return raw decoded text.

    Cleaning / validation lives in qg_core, shared with the HF Space.
    """
    if _local_model is None or _local_tokenizer is None:
        raise RuntimeError("Local model not loaded")

    inputs = _local_tokenizer(
        prompt,
        return_tensors="pt",
        max_length=_MAX_INPUT_LENGTH,
        truncation=True,
    )
    outputs = _local_model.generate(
        **inputs,
        max_length=_MAX_OUTPUT_LENGTH,
        num_beams=_NUM_BEAMS,
        repetition_penalty=_REPETITION_PENALTY,
        no_repeat_ngram_size=_NO_REPEAT_NGRAM_SIZE,
        early_stopping=True,
    )
    return _local_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def _generate_locally(material_text: str, num_questions: int | None = None) -> list[dict]:
    """Local CPU fallback when HF Space unavailable. Uses the same answer-aware
    assembly as the Space, so the correct answer always answers the question."""
    n = num_questions if num_questions is not None else _NUM_QUESTIONS
    rng = random.Random(abs(hash(material_text)) & 0xFFFFFFFF)
    questions = qg_core.build_quiz(
        material_text, _run_local_model, num_questions=n, rng=rng
    )
    if not questions:
        raise RuntimeError("Failed to generate any valid questions locally")
    logger.info("ml.generator: local CPU produced %d questions", len(questions))
    return questions


if __name__ == "__main__":
    sample = (
        "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau "
        "dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di "
        "kloroplas dan menghasilkan oksigen sebagai produk samping. Reaksi "
        "terang berlangsung di tilakoid, sedangkan reaksi gelap berlangsung "
        "di stroma."
    )
    print(f"HF_SPACE_URL: {_HF_SPACE_URL or '(not set)'}")
    if not is_available():
        print("Both HF Space and local model unavailable")
    else:
        print(f"Generating quiz from sample ({len(sample)} chars)...")
        try:
            quiz = generate(sample)
            for i, q in enumerate(quiz, 1):
                print(f"\nQ{i}: {q['question']}")
                for j, opt in enumerate(q["options"]):
                    marker = " ✓" if j == q["correct_option_index"] else "  "
                    print(f" {chr(65 + j)}.{marker} {opt}")
        except RuntimeError as exc:
            print(f"Failed: {exc}")
