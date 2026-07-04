"""Train the understanding classifier (sklearn Random Forest).

OWNER: Desta

Run as a module from `backend/`:
    python -m ml.classifier.train

This will:
    1. Generate 10k synthetic samples
    2. Split 80/20 train/test
    3. Train RandomForestClassifier
    4. Print accuracy, classification report, feature importances
    5. Save model to ml/classifier/artifacts/classifier.pkl

After training, COMMIT the .pkl artifact (it's small, < 5MB).
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from ml.classifier.data_generation import (
    describe_dataset,
    generate_synthetic_data,
)


# Hyperparameters. Tuned for ~94% test accuracy with 5% noise injection.
N_ESTIMATORS = 100
MAX_DEPTH = 10
RANDOM_STATE = 42
TEST_SIZE = 0.2

FEATURE_NAMES = [
    "score_percentage",
    "time_taken_seconds",
    "wrong_count",
    "unanswered_count",
]

ARTIFACT_DIR = Path(__file__).parent / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "classifier.pkl"


def train_and_save() -> RandomForestClassifier:
    """Train the model and save the artifact. Return the fitted model."""
    print("Generating synthetic dataset...")
    X, y = generate_synthetic_data()
    print(describe_dataset(X, y))
    print()

    print("Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test:  {len(X_test)} samples")
    print()

    print(f"Training RandomForestClassifier(n={N_ESTIMATORS}, max_depth={MAX_DEPTH})...")
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print("  Training done.")
    print()

    print("=" * 50)
    print("Test set evaluation")
    print("=" * 50)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print()
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix:")
    labels_sorted = sorted(set(y_test))
    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)
    print("  " + " ".join(f"{l:>8s}" for l in labels_sorted))
    for label, row in zip(labels_sorted, cm, strict=True):
        print(f"  {label:>6s}  " + " ".join(f"{v:>7d}" for v in row))
    print()

    print("Feature importances:")
    for name, importance in sorted(
        zip(FEATURE_NAMES, model.feature_importances_, strict=True),
        key=lambda x: -x[1],
    ):
        print(f"  {name:25s} {importance:.4f}")
    print()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACT_PATH)
    print(f"Saved model to: {ARTIFACT_PATH}")
    print(f"Artifact size: {ARTIFACT_PATH.stat().st_size / 1024:.1f} KB")

    return model


if __name__ == "__main__":
    train_and_save()
