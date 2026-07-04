"""Synthetic dataset generator for the understanding classifier.

OWNER: Desta

Generates ~10,000 samples of (features → label) pairs by applying rule-based
labeling with noise injection. The trained model then learns to generalize
the rule + handle ambiguous cases.

Why synthetic: we don't have real user quiz data yet. Rule-based labeling +
noise gives us a ground truth that the model can imitate while still
handling boundary cases.

Run as a module:
    python -m ml.classifier.data_generation

Run from this file (smoke test):
    python ml/classifier/data_generation.py
"""

from __future__ import annotations

import numpy as np


# Tunable knobs — Desta, adjust based on real data later (post-MVP).
DEFAULT_N = 10_000
DEFAULT_SEED = 42
NOISE_RATE = 0.05  # 5% of samples get a randomly-flipped label

# Label thresholds — match the rule-based logic in PRD.md §15.
# These are USED to label synthetic data; the trained model learns from them.
HIGH_SCORE_THRESHOLD = 80
MEDIUM_SCORE_THRESHOLD = 50
SECONDS_PER_QUESTION_BASELINE = 60
HIGH_TIME_MULTIPLIER = 6.0

# Feature ranges (realistic for quiz with 5 questions).
FEATURE_RANGES = {
    "score_percentage": (0, 100),
    "time_taken_seconds": (10, 1800),  # 10s-30min: covers fast completions
    # (one-question flow + keyboard shortcuts let users finish well under 60s)
    "wrong_count": (0, 11),
    "unanswered_count": (0, 6),
}

LABELS = ("high", "medium", "low")


def _label_from_rules(
    score: float,
    time: float,
    total_questions: int = 5,
) -> str:
    """Deterministic rule-based labeling. Mirrors PRD.md §15.

    Used as ground truth for training data generation.
    """
    reasonable_time = total_questions * SECONDS_PER_QUESTION_BASELINE
    if score >= HIGH_SCORE_THRESHOLD and time <= reasonable_time * HIGH_TIME_MULTIPLIER:
        return "high"
    if score >= MEDIUM_SCORE_THRESHOLD:
        return "medium"
    return "low"


def generate_synthetic_data(
    n: int = DEFAULT_N,
    seed: int = DEFAULT_SEED,
    noise_rate: float = NOISE_RATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate (X, y) for sklearn training.

    Args:
        n: number of samples
        seed: rng seed for reproducibility
        noise_rate: probability of flipping a label to a random other class

    Returns:
        X: (n, 4) float array — score_percentage, time_taken_seconds, wrong_count, unanswered_count
        y: (n,) string array — "high" | "medium" | "low"
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n, 4), dtype=np.float64)
    y = np.empty(n, dtype=object)

    for i in range(n):
        score = rng.uniform(*FEATURE_RANGES["score_percentage"])
        time = rng.uniform(*FEATURE_RANGES["time_taken_seconds"])
        wrong = rng.integers(*FEATURE_RANGES["wrong_count"])
        unans = rng.integers(*FEATURE_RANGES["unanswered_count"])

        baseline_label = _label_from_rules(score, time)

        # Inject noise: with probability noise_rate, flip to a random other class
        if rng.random() < noise_rate:
            other_labels = [l for l in LABELS if l != baseline_label]
            label = str(rng.choice(other_labels))
        else:
            label = baseline_label

        X[i] = [score, time, wrong, unans]
        y[i] = label

    return X, y


def describe_dataset(X: np.ndarray, y: np.ndarray) -> str:
    """Return a human-readable summary of the dataset for sanity checking."""
    lines: list[str] = []
    lines.append(f"Total samples: {len(X)}")
    unique, counts = np.unique(y, return_counts=True)
    lines.append("Label distribution:")
    for label, count in zip(unique, counts, strict=True):
        pct = 100 * count / len(y)
        lines.append(f"  {label:6s}: {count:5d} ({pct:.1f}%)")
    lines.append(
        f"Score range: [{X[:, 0].min():.1f}, {X[:, 0].max():.1f}], "
        f"mean={X[:, 0].mean():.1f}"
    )
    lines.append(
        f"Time range:  [{X[:, 1].min():.0f}, {X[:, 1].max():.0f}]s, "
        f"mean={X[:, 1].mean():.0f}s"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    X, y = generate_synthetic_data()
    print(describe_dataset(X, y))
