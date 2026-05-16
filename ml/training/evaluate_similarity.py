"""
evaluate_similarity.py

Baseline evaluation of whether USE cosine similarity scores
correlate with the human-curated quality labels in the dataset.

Pipeline per sample:
    ideal_answer → embedding
    candidate_answer → embedding
    cosine_similarity → predicted score
    |predicted - label| → absolute error

This script does NOT train anything.
It validates that the semantic pipeline behaves as expected.
"""

import sys
import logging
from pathlib import Path
from collections import defaultdict

import numpy as np

# ---------------------------------------------------------------------------
# Path setup — allow running from project root or ml/ directory
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ml.training.dataset_loader import load_training_samples
from backend.app.ml.embeddings.use_embeddings import encode_batch
from backend.app.ml.embeddings.similarity import batch_similarity

logging.basicConfig(level=logging.WARNING)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate() -> None:
    print("=" * 60)
    print("  USE Semantic Similarity — Baseline Evaluation")
    print("=" * 60)

    # ── 1. Load dataset ──────────────────────────────────────────
    print("\nLoading training samples...")
    samples = load_training_samples()
    total = len(samples)
    print(f"  Loaded {total} samples.\n")

    # ── 2. Batch-encode all ideal and candidate answers ──────────
    print("Encoding ideal answers...")
    ideal_texts     = [s["ideal_answer"]     for s in samples]
    candidate_texts = [s["candidate_answer"] for s in samples]

    ideal_embeddings     = encode_batch(ideal_texts)
    print("Encoding candidate answers...")
    candidate_embeddings = encode_batch(candidate_texts)

    # ── 3. Compute similarities and errors ───────────────────────
    print("Computing similarity scores...\n")
    similarities = batch_similarity(ideal_embeddings, candidate_embeddings)
    labels       = np.array([s["label"] for s in samples], dtype=np.float32)
    errors       = np.abs(similarities - labels)

    # ── 4. Overall metrics ───────────────────────────────────────
    print("-" * 60)
    print(f"  Total samples      : {total}")
    print(f"  Average similarity : {similarities.mean():.4f}")
    print(f"  Average label      : {labels.mean():.4f}")
    print(f"  Avg absolute error : {errors.mean():.4f}")
    print(f"  Min similarity     : {similarities.min():.4f}")
    print(f"  Max similarity     : {similarities.max():.4f}")
    print("-" * 60)

    # ── 5. Per-quality group breakdown ───────────────────────────
    quality_order = ["excellent", "good", "average", "weak"]
    group_sims:   dict[str, list[float]] = defaultdict(list)
    group_labels: dict[str, list[float]] = defaultdict(list)
    group_errors: dict[str, list[float]] = defaultdict(list)

    for i, sample in enumerate(samples):
        q = sample["quality"]
        group_sims[q].append(float(similarities[i]))
        group_labels[q].append(float(labels[i]))
        group_errors[q].append(float(errors[i]))

    print(f"\n{'Quality':<12} {'N':>4}  {'Avg Label':>10}  {'Avg Sim':>8}  {'Avg Error':>10}")
    print("-" * 52)
    for quality in quality_order:
        sims   = group_sims.get(quality, [])
        labs   = group_labels.get(quality, [])
        errs   = group_errors.get(quality, [])
        if not sims:
            continue
        print(
            f"  {quality:<10} {len(sims):>4}  "
            f"{np.mean(labs):>10.4f}  "
            f"{np.mean(sims):>8.4f}  "
            f"{np.mean(errs):>10.4f}"
        )

    # ── 6. Example comparisons ───────────────────────────────────
    print("\n" + "-" * 60)
    print("  Sample comparisons (one per quality tier)")
    print("-" * 60)

    shown: set[str] = set()
    for i, sample in enumerate(samples):
        q = sample["quality"]
        if q in shown:
            continue
        shown.add(q)

        print(f"\n  [{q.upper()}]")
        print(f"  Question  : {sample['question'][:70]}")
        print(f"  Ideal     : {sample['ideal_answer'][:70]}")
        print(f"  Candidate : {sample['candidate_answer'][:70]}")
        print(f"  Label     : {labels[i]:.2f}  |  "
              f"Similarity: {similarities[i]:.4f}  |  "
              f"Error: {errors[i]:.4f}")

        if len(shown) == len(quality_order):
            break

    print("\n" + "=" * 60)
    print("  Evaluation complete.")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    evaluate()