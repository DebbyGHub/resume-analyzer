"""
answer_quality.py

High-level orchestrator for interview answer evaluation.

Combines:
  - semantic similarity  (70%)
  - confidence estimate  (30%)
into a single final_score, then classifies quality.

This module does NOT implement any ML training or NLP parsing.
It delegates to similarity.py and confidence_estimator.py.
"""

from typing import Literal

from backend.app.ml.embeddings.similarity import similarity_from_texts
from backend.app.ml.evaluation.confidence_estimator import estimate_confidence

# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

_SIMILARITY_WEIGHT  = 0.80
_CONFIDENCE_WEIGHT  = 0.20

# ---------------------------------------------------------------------------
# Quality thresholds
# ---------------------------------------------------------------------------

_THRESHOLDS: list[tuple[float, str]] = [
    (0.72, "excellent"),
    (0.56, "good"),
    (0.38, "average"),
    (0.00, "weak"),
]


def _classify_quality(score: float) -> Literal["excellent", "good", "average", "weak"]:
    for threshold, label in _THRESHOLDS:
        if score >= threshold:
            return label  # type: ignore[return-value]
    return "weak"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_answer(
    ideal_answer: str,
    candidate_answer: str,
) -> dict:
    """
    Evaluate a candidate answer against an ideal answer.

    Args:
        ideal_answer:      The reference/expected answer.
        candidate_answer:  The candidate's response.

    Returns:
        {
            "similarity_score": float,   # cosine similarity [0, 1]
            "confidence_score": float,   # adjusted confidence [0, 1]
            "final_score":      float,   # weighted combination [0, 1]
            "quality":          str,     # excellent | good | average | weak
            "flags":            list[str]
        }
    """
    # ── Step 1: semantic similarity ──────────────────────────────
    similarity_score = similarity_from_texts(ideal_answer, candidate_answer)

    # ── Step 2: confidence estimation ────────────────────────────
    confidence_result = estimate_confidence(similarity_score, candidate_answer)
    confidence_score  = confidence_result["confidence_score"]
    flags             = confidence_result["flags"]

    # ── Step 3: weighted final score ─────────────────────────────
    final_score = round(
        _SIMILARITY_WEIGHT * similarity_score
        + _CONFIDENCE_WEIGHT * confidence_score,
        4,
    )
    final_score = max(0.0, min(1.0, final_score))

    # ── Step 4: quality classification ───────────────────────────
    quality = _classify_quality(final_score)

    return {
        "similarity_score": round(similarity_score, 4),
        "confidence_score": round(confidence_score, 4),
        "final_score":      final_score,
        "quality":          quality,
        "flags":            flags,
    }

if __name__ == "__main__":

    ideal = (
        "Encapsulation hides internal implementation details "
        "and protects object state."
    )

    answers = [
        "Encapsulation hides implementation details and protects data.",
        "Used for security.",
        "Yes.",
        "",
    ]

    for ans in answers:
        result = evaluate_answer(ideal, ans)

        print("\n" + "-" * 60)
        print("Answer :", repr(ans))
        print("Result :", result)