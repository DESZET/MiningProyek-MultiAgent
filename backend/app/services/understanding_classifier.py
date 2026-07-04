"""Understanding classifier — maps EvaluationResult to UnderstandingLevel.

OWNER: Desta (Backend — Logic, Insight & Recommendation)

This is a THIN WRAPPER around `ml/classifier/inference.py` (sklearn Random Forest).
The wrapper:
    1. Extracts features from EvaluationResult
    2. Tries ML inference via ml.classifier
    3. Falls back to rule-based threshold logic if ML is unavailable

The actual model loading + prediction lives in
`backend/ml/classifier/inference.py`. See ML.md §4 for details.

If you want to swap the ML approach (e.g., XGBoost, NN), edit
`ml/classifier/{train,inference}.py`. This wrapper file should rarely change.
"""

from __future__ import annotations

import logging

from app.schemas.internal import EvaluationResult
from app.schemas.result import UnderstandingLevel
from ml.classifier import inference as ml_classifier

logger = logging.getLogger(__name__)

# Rule-based fallback thresholds (mirror PRD.md §15 + ml/classifier/data_generation.py)
HIGH_SCORE_THRESHOLD = 80
MEDIUM_SCORE_THRESHOLD = 50
SECONDS_PER_QUESTION_BASELINE = 60
HIGH_TIME_MULTIPLIER = 6.0


# Severity ordering for guardrail clamping.
_LEVEL_SEVERITY = {
    UnderstandingLevel.LOW: 0,
    UnderstandingLevel.MEDIUM: 1,
    UnderstandingLevel.HIGH: 2,
}


def _score_ceiling(score: int) -> UnderstandingLevel:
    """Highest understanding level a given score can justify."""
    if score >= HIGH_SCORE_THRESHOLD:
        return UnderstandingLevel.HIGH
    if score >= MEDIUM_SCORE_THRESHOLD:
        return UnderstandingLevel.MEDIUM
    return UnderstandingLevel.LOW


def _clamp_to_score(level: UnderstandingLevel, score: int) -> UnderstandingLevel:
    """Guardrail: the model must not claim a higher level than the score allows.

    The Random Forest was trained on time_taken_seconds in [60, 1800]. Very fast
    completions (e.g. 29s) are out-of-distribution and the model can wrongly
    output 'high' for a low score. This keeps classification honest and
    reviewable (PRD product rule) without retraining. The model may still
    DOWNGRADE (e.g. high score but slow/hesitant -> medium).
    """
    ceiling = _score_ceiling(score)
    if _LEVEL_SEVERITY[level] > _LEVEL_SEVERITY[ceiling]:
        return ceiling
    return level


def classify(eval_result: EvaluationResult) -> UnderstandingLevel:
    """Apply ML or fallback rule-based classification.

    Tries the trained Random Forest first. Falls back to rule-based
    thresholds if model not loaded. ML output is clamped by the score
    ceiling as a guardrail against out-of-distribution inputs.
    """
    # === Path 1: ML via ml/classifier (preferred) ===
    if ml_classifier.is_available():
        try:
            features = [
                float(eval_result.score_percentage),
                float(eval_result.time_taken_seconds),
                float(eval_result.wrong_count),
                float(eval_result.unanswered_count),
            ]
            label_str = ml_classifier.predict(features)
            level = UnderstandingLevel(label_str)
            return _clamp_to_score(level, eval_result.score_percentage)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "understanding_classifier: ML path failed (%s), falling back to rule-based",
                exc,
            )

    # === Path 2: rule-based fallback ===
    return _classify_rule_based(eval_result)


def _classify_rule_based(eval_result: EvaluationResult) -> UnderstandingLevel:
    """Rule-based classification (PRD.md §15). Used as fallback."""
    score = eval_result.score_percentage
    time = eval_result.time_taken_seconds
    total = eval_result.total_questions

    reasonable_time = total * SECONDS_PER_QUESTION_BASELINE
    time_within_high_window = time <= reasonable_time * HIGH_TIME_MULTIPLIER

    if score >= HIGH_SCORE_THRESHOLD and time_within_high_window:
        return UnderstandingLevel.HIGH
    if score >= MEDIUM_SCORE_THRESHOLD:
        return UnderstandingLevel.MEDIUM
    return UnderstandingLevel.LOW
