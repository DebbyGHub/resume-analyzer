"""
confidence_estimator.py

Rule-based confidence estimation for semantic similarity scores.

Determines how much to trust a similarity score by inspecting:
  - answer length (too short = less reliable)
  - vague/generic phrasing patterns
  - empty or near-empty input

This is NOT a classifier and does NOT use any ML model.
All logic is deterministic and explainable.
"""

import re
from typing import Literal

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Word count thresholds
_MIN_WORDS_FULL_CONFIDENCE  = 10   # answers below this get a length penalty
_MIN_WORDS_LOW_CONFIDENCE   = 4    # answers below this get a severe penalty
_EMPTY_THRESHOLD_WORDS      = 1    # 0 or 1 word → treat as empty

# Confidence level boundaries (applied to final confidence_score)
_LEVEL_HIGH_THRESHOLD   = 0.75
_LEVEL_MEDIUM_THRESHOLD = 0.50

# Vague phrase patterns — single-line, case-insensitive
_VAGUE_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^i\s+(think|believe|guess|feel)\s+(so|it|this)?\s*$",
        r"^(it|this)\s+(is|was)\s+used\s+for\s+\w+\s*$",
        r"^it\s+improve[sd]?\s+(performance|speed|security|efficiency)\s*$",
        r"^(not\s+sure|i\s+don'?t\s+know|i\s+don'?t\s+remember)\s*",
        r"^(it'?s?\s+)?(basically|just|simply|kind\s+of|sort\s+of)",
        r"^(yes|no|maybe|correct|true|false)\s*$",
        r"^i\s+(have\s+)?heard\s+of\s+(it|this)\s+but",
        r"^it\s+helps\s+with\s+(the\s+)?\w+\s*$",
        r"^(something|stuff)\s+(related\s+to|about|like)\s+",
    ]
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _word_count(text: str) -> int:
    return len(text.split()) if text and text.strip() else 0


def _is_vague(text: str) -> bool:
    """Return True if the answer matches any known vague-phrase pattern."""
    stripped = text.strip()
    return any(p.search(stripped) for p in _VAGUE_PATTERNS)


def _confidence_level(
    score: float,
) -> Literal["high", "medium", "low"]:
    if score >= _LEVEL_HIGH_THRESHOLD:
        return "high"
    if score >= _LEVEL_MEDIUM_THRESHOLD:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_length_penalty(candidate_answer: str) -> float:
    """
    Return a penalty value in [0.0, 1.0] based on answer length.

    0.0  = no penalty (answer is long enough)
    0.3  = mild penalty (short but present)
    0.6  = heavy penalty (very short)
    1.0  = maximum penalty (empty)
    """
    words = _word_count(candidate_answer)

    if words <= _EMPTY_THRESHOLD_WORDS:
        return 1.0
    if words < _MIN_WORDS_LOW_CONFIDENCE:
        return 0.60
    if words < _MIN_WORDS_FULL_CONFIDENCE:
        # Linear interpolation: 0.30 at 4 words → 0.0 at 10 words
        progress = (words - _MIN_WORDS_LOW_CONFIDENCE) / (
            _MIN_WORDS_FULL_CONFIDENCE - _MIN_WORDS_LOW_CONFIDENCE
        )
        return round(0.30 * (1.0 - progress), 4)
    return 0.0


def estimate_confidence(
    similarity_score: float,
    candidate_answer: str,
) -> dict:
    """
    Estimate confidence in a semantic similarity score.

    Args:
        similarity_score: Cosine similarity in [0.0, 1.0].
        candidate_answer: Raw candidate answer text.

    Returns:
        {
            "confidence_score":  float in [0.0, 1.0],
            "confidence_level":  "high" | "medium" | "low",
            "length_penalty":    float in [0.0, 1.0],
            "flags":             list[str]  — human-readable warnings
        }
    """
    flags: list[str] = []
    words = _word_count(candidate_answer)

    # ── Guard: empty answer ──────────────────────────────────────
    if words <= _EMPTY_THRESHOLD_WORDS:
        return {
            "confidence_score": 0.0,
            "confidence_level": "low",
            "length_penalty":   1.0,
            "flags":            ["empty_answer"],
        }

    # ── Length penalty ───────────────────────────────────────────
    length_penalty = calculate_length_penalty(candidate_answer)

    if words < _MIN_WORDS_LOW_CONFIDENCE:
        flags.append("answer_too_short")
    elif words < _MIN_WORDS_FULL_CONFIDENCE:
        flags.append("answer_brief")

    # ── Vague phrase detection ───────────────────────────────────
    vague_penalty = 0.0
    if _is_vague(candidate_answer):
        vague_penalty = 0.25
        flags.append("vague_answer")

    # ── Confidence score ─────────────────────────────────────────
    # Start from the similarity score, then reduce by penalties.
    # Penalties are additive; total reduction capped at 0.80 to
    # avoid collapsing a genuinely high-sim answer to near-zero.
    total_penalty  = min(length_penalty + vague_penalty, 0.80)
    confidence_raw = similarity_score * (1.0 - total_penalty)
    confidence_score = round(max(0.0, min(1.0, confidence_raw)), 4)

    return {
        "confidence_score": confidence_score,
        "confidence_level": _confidence_level(confidence_score),
        "length_penalty":   length_penalty,
        "flags":            flags,
    }
