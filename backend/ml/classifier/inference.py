"""Inference for the understanding classifier.

OWNER: Desta

Loads the trained sklearn model at module import. Provides a `predict()`
function called from `app/services/understanding_classifier.py`.

If the model artifact is missing or fails to load, this module sets
`_USE_ML = False` and the wrapper service will fall back to rule-based
classification.

The wrapper (in app/services/) is responsible for handling the fallback;
this module just exposes whether ML is available and the predict function.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ARTIFACT_PATH = Path(__file__).parent / "artifacts" / "classifier.pkl"

# Module-level state: loaded once at import, reused across requests.
_model = None
_load_error: Optional[str] = None


def _load_model() -> None:
    """Try to load the model. Set _model on success, _load_error on failure."""
    global _model, _load_error
    try:
        import joblib

        if not ARTIFACT_PATH.exists():
            _load_error = f"Model artifact not found at {ARTIFACT_PATH}"
            logger.warning("ml.classifier: %s — fallback to rule-based", _load_error)
            return
        _model = joblib.load(ARTIFACT_PATH)
        logger.info(
            "ml.classifier: Loaded classifier from %s (sklearn %s)",
            ARTIFACT_PATH,
            type(_model).__name__,
        )
    except Exception as exc:  # noqa: BLE001
        _load_error = f"{type(exc).__name__}: {exc}"
        logger.warning(
            "ml.classifier: Failed to load model (%s) — fallback to rule-based",
            _load_error,
        )


# Load eagerly at import time
_load_model()


def is_available() -> bool:
    """Return True if the ML model is loaded and ready for inference."""
    return _model is not None


def predict(features: list[float]) -> str:
    """Predict understanding level from feature vector.

    Args:
        features: [score_percentage, time_taken_seconds, wrong_count, unanswered_count]

    Returns:
        One of "high", "medium", "low".

    Raises:
        RuntimeError: if the model isn't loaded. Caller should check is_available()
            first and use the rule-based fallback if False.
    """
    if _model is None:
        raise RuntimeError(
            f"ml.classifier model not available: {_load_error}. "
            "Call is_available() first and use rule-based fallback."
        )
    prediction = _model.predict([features])[0]
    return str(prediction)


if __name__ == "__main__":
    # Smoke test: predict a few sample inputs
    if not is_available():
        print(f"Model not available: {_load_error}")
        print("Run: python -m ml.classifier.train")
    else:
        samples = [
            ([95.0, 200.0, 0.0, 0.0], "expected: high"),
            ([60.0, 500.0, 2.0, 0.0], "expected: medium"),
            ([20.0, 400.0, 4.0, 2.0], "expected: low"),
        ]
        for features, note in samples:
            label = predict(features)
            print(f"  features={features} → {label}  ({note})")
