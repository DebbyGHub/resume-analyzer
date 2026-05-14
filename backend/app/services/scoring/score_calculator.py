"""
score_calculator.py

Responsibilities:
- Own the mode-specific weight tables
- Orchestrate the full scoring pipeline
- Produce the final ScoreResult

This is the only module that knows about weights.
section_scorer and keyword_matcher produce 0–100 sub-scores independently.
"""

from typing import Optional
from app.schemas.resume_schema import DetectedSections, SectionCounts
from app.schemas.scoring_schema import ScoreBreakdown, ScoreResult
from app.services.scoring.keyword_matcher import (
    detect_mode,
    resolve_title_to_role,
    get_keywords_for_role,
    extract_keywords_from_jd,
    match_keywords,
)
from app.services.scoring.section_scorer import score_sections, score_structure


# ---------------------------------------------------------------------------
# Weight tables — one per mode, must each sum to 1.0
# ---------------------------------------------------------------------------

_WEIGHTS: dict[str, dict[str, float]] = {
    "job_title": {
        "keyword":   0.30,
        "section":   0.40,
        "structure": 0.30,
    },
    "ats": {
        "keyword":   0.60,
        "section":   0.20,
        "structure": 0.20,
    },
}

for _mode, _w in _WEIGHTS.items():
    assert abs(sum(_w.values()) - 1.0) < 1e-9, f"Weights for mode '{_mode}' must sum to 1.0"


# ---------------------------------------------------------------------------
# Keyword score: raw match ratio → 0–100
# ---------------------------------------------------------------------------

def _keyword_raw_score(matched: list[str], total_keywords: int) -> int:
    """
    Convert a match count into a 0–100 score.
    Returns 0 when no keywords are defined (avoids division by zero).
    """
    if total_keywords == 0:
        return 0
    ratio = len(matched) / total_keywords
    return min(100, round(ratio * 100))


# ---------------------------------------------------------------------------
# Public orchestrator
# ---------------------------------------------------------------------------

def calculate_score(
    resume_text: str,
    job_title: str,
    job_description: Optional[str],
    sections: DetectedSections,
    counts: SectionCounts,
) -> ScoreResult:
    """
    Full scoring pipeline.

    Flow:
    1. Detect mode
    2. Build keyword list (role lookup in job_title mode; JD extraction in ats mode)
    3. Match keywords against resume text
    4. Score sections and structure (independent of mode)
    5. Apply mode-specific weights
    6. Return ScoreResult
    """
    mode = detect_mode(job_description)
    weights = _WEIGHTS[mode]

    # --- Keyword resolution ---
    if mode == "ats":
        target_keywords = extract_keywords_from_jd(job_description)  # type: ignore[arg-type]
    else:
        role_key = resolve_title_to_role(job_title)
        target_keywords = get_keywords_for_role(role_key) if role_key else []

    matched_keywords, missing_keywords = match_keywords(resume_text, target_keywords)

    # --- Sub-scores (each 0–100) ---
    raw_keyword   = _keyword_raw_score(matched_keywords, len(target_keywords))
    raw_section   = score_sections(sections, counts)
    raw_structure = score_structure(sections, counts)

    # --- Weighted contributions (scale each sub-score by weight × 100) ---
    keyword_contrib   = round(raw_keyword   * weights["keyword"])
    section_contrib   = round(raw_section   * weights["section"])
    structure_contrib = round(raw_structure * weights["structure"])

    # --- Total (sum of weighted contributions; naturally ≤ 100) ---
    total = min(100, keyword_contrib + section_contrib + structure_contrib)

    return ScoreResult(
        mode=mode,
        total_score=total,
        score_breakdown=ScoreBreakdown(
            keyword_score=keyword_contrib,
            section_score=section_contrib,
            structure_score=structure_contrib,
        ),
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
    )