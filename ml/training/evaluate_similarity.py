"""
evaluate_similarity.py

Baseline evaluation for the semantic interview evaluator.

This script:
- loads training samples
- generates USE embeddings
- computes cosine similarity
- compares similarity against dynamically-generated labels

No model training happens here.
This is purely for evaluator calibration and debugging.
"""

import sys
import logging
from pathlib import Path
from collections import defaultdict

import numpy as np

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------

from ml.training.dataset_loader import load_training_samples

from backend.app.ml.embeddings.use_embeddings import (
    encode_batch,
)

from backend.app.ml.embeddings.similarity import (
    batch_similarity,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.WARNING)

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_THRESHOLDS: list[tuple[float, str]] = [
    (0.78, "excellent"),
    (0.62, "good"),
    (0.42, "average"),
    (0.00, "weak"),
]

# ---------------------------------------------------------------------------
# Similarity → predicted quality
# ---------------------------------------------------------------------------

def similarity_to_quality(score: float) -> str:

    for threshold, label in _THRESHOLDS:
        if score >= threshold:
            return label

    return "weak"

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate() -> None:

    print("=" * 60)
    print("  USE Semantic Similarity — Baseline Evaluation")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 1. Load dataset
    # -----------------------------------------------------------------------

    print("\nLoading training samples...")

    samples = load_training_samples()

    total = len(samples)

    print(f"  Loaded {total} samples.\n")

    # -----------------------------------------------------------------------
    # 2. Extract texts
    # -----------------------------------------------------------------------

    ideal_texts = [
        sample["ideal_answer"]
        for sample in samples
    ]

    candidate_texts = [
        sample["candidate_answer"]
        for sample in samples
    ]

    # -----------------------------------------------------------------------
    # 3. Encode embeddings
    # -----------------------------------------------------------------------

    print("Encoding ideal answers...")

    ideal_embeddings = encode_batch(ideal_texts)

    print("Encoding candidate answers...")

    candidate_embeddings = encode_batch(candidate_texts)

    # -----------------------------------------------------------------------
    # 4. Similarity
    # -----------------------------------------------------------------------

    print("Computing similarity scores...\n")

    similarities = batch_similarity(
        ideal_embeddings,
        candidate_embeddings,
    )

    labels = np.array(
        [sample["label"] for sample in samples],
        dtype=np.float32,
    )

    errors = np.abs(similarities - labels)

    # -----------------------------------------------------------------------
    # 5. Overall metrics
    # -----------------------------------------------------------------------

    print("-" * 60)

    print(f"  Total samples      : {total}")

    print(f"  Average similarity : {similarities.mean():.4f}")

    print(f"  Average label      : {labels.mean():.4f}")

    print(f"  Avg absolute error : {errors.mean():.4f}")

    print(f"  Min similarity     : {similarities.min():.4f}")

    print(f"  Max similarity     : {similarities.max():.4f}")

    print("-" * 60)

    # -----------------------------------------------------------------------
    # 6. Per-quality breakdown
    # -----------------------------------------------------------------------

    quality_order = [
        "excellent",
        "good",
        "average",
        "weak",
    ]

    group_sims: dict[str, list[float]] = defaultdict(list)

    group_labels: dict[str, list[float]] = defaultdict(list)

    group_errors: dict[str, list[float]] = defaultdict(list)

    for i, sample in enumerate(samples):

        quality = sample["quality"]

        group_sims[quality].append(
            float(similarities[i])
        )

        group_labels[quality].append(
            float(labels[i])
        )

        group_errors[quality].append(
            float(errors[i])
        )

    print(
        f"\n{'Quality':<12} {'N':>4}  "
        f"{'Avg Label':>10}  "
        f"{'Avg Sim':>8}  "
        f"{'Avg Error':>10}"
    )

    print("-" * 52)

    for quality in quality_order:

        sims = group_sims.get(quality, [])

        labs = group_labels.get(quality, [])

        errs = group_errors.get(quality, [])

        if not sims:
            continue

        print(
            f"  {quality:<10} {len(sims):>4}  "
            f"{np.mean(labs):>10.4f}  "
            f"{np.mean(sims):>8.4f}  "
            f"{np.mean(errs):>10.4f}"
        )

    # -----------------------------------------------------------------------
    # 7. Quality prediction accuracy
    # -----------------------------------------------------------------------

    predicted_qualities = [
        similarity_to_quality(score)
        for score in similarities
    ]

    actual_qualities = [
        sample["quality"]
        for sample in samples
    ]

    correct = sum(
        predicted == actual
        for predicted, actual
        in zip(predicted_qualities, actual_qualities)
    )

    accuracy = correct / total

    print("\n" + "-" * 60)

    print(f"  Quality classification accuracy: {accuracy:.4f}")

    print("-" * 60)

    # -----------------------------------------------------------------------
    # 8. Example comparisons
    # -----------------------------------------------------------------------

    print("\nSample comparisons:")
    print("-" * 60)

    shown: set[str] = set()

    for i, sample in enumerate(samples):

        quality = sample["quality"]

        if quality in shown:
            continue

        shown.add(quality)

        predicted_quality = similarity_to_quality(
            float(similarities[i])
        )

        print(f"\n[{quality.upper()}]")

        print(f"Question:")
        print(f"  {sample['question']}")

        print(f"\nIdeal:")
        print(f"  {sample['ideal_answer']}")

        print(f"\nCandidate:")
        print(f"  {sample['candidate_answer']}")

        print(
            f"\nExpected   : {quality}"
        )

        print(
            f"Predicted  : {predicted_quality}"
        )

        print(
            f"Similarity : {similarities[i]:.4f}"
        )

        print(
            f"Label      : {labels[i]:.2f}"
        )

        print(
            f"Error      : {errors[i]:.4f}"
        )

        if len(shown) == len(quality_order):
            break

    # -----------------------------------------------------------------------
    # Done
    # -----------------------------------------------------------------------

    print("\n" + "=" * 60)

    print("  Evaluation complete.")

    print("=" * 60 + "\n")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    evaluate()