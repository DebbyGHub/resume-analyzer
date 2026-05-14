"""
section_scorer.py

Responsibilities:
- Score resume section presence and completeness
- Score resume structure quality
- Return raw sub-scores (0–100 scale) before weighting

All scoring is deterministic and rule-based.
The caller (score_calculator.py) applies mode-specific weights.
"""

from app.schemas.resume_schema import DetectedSections, SectionCounts


# ---------------------------------------------------------------------------
# Section presence scoring
# ---------------------------------------------------------------------------

# Maximum points awarded per section (must sum to 100)
_SECTION_WEIGHTS: dict[str, int] = {
    "experience":     35,
    "skills":         25,
    "education":      20,
    "projects":       10,
    "summary":         5,
    "certifications":  5,
}
assert sum(_SECTION_WEIGHTS.values()) == 100, "Section weights must sum to 100"


def score_sections(sections: DetectedSections, counts: SectionCounts) -> int:
    """
    Return a section presence score (0–100).

    Scoring rules per section:
    - experience:      present → full points; augmented if ≥ 2 entries
    - skills:          present → full points
    - education:       present → full points
    - projects:        present → full points; augmented if ≥ 2 entries
    - summary:         present → full points
    - certifications:  present → full points

    The section score is additive — missing sections simply contribute 0.
    """
    score = 0.0
    section_data = sections.model_dump()

    for section_name, weight in _SECTION_WEIGHTS.items():
        body = section_data.get(section_name)
        if not body:
            continue

        section_score = float(weight)

        # Bonus for experience depth (up to 10% of section weight)
        if section_name == "experience" and counts.experience_entries >= 2:
            section_score = min(weight, section_score * 1.10)

        # Bonus for project breadth (up to 10% of section weight)
        if section_name == "projects" and counts.project_entries >= 2:
            section_score = min(weight, section_score * 1.10)

        score += section_score

    return min(100, round(score))


# ---------------------------------------------------------------------------
# Structure quality scoring
# ---------------------------------------------------------------------------

def score_structure(sections: DetectedSections, counts: SectionCounts) -> int:
    """
    Return a structure quality score (0–100) based on:

    | Criterion                                  | Points |
    |--------------------------------------------|--------|
    | Has both experience AND education           |   25   |
    | Has skills section                          |   20   |
    | Has at least 1 project entry               |   20   |
    | Has a summary/objective                     |   15   |
    | Experience has ≥ 2 entries (depth signal)  |   10   |
    | Has certifications                          |   10   |
    |--------------------------------------------|--------|
    | Total                                       |  100   |
    """
    score = 0

    if sections.experience and sections.education:
        score += 25

    if sections.skills:
        score += 20

    if sections.projects and counts.project_entries >= 1:
        score += 20

    if sections.summary:
        score += 15

    if counts.experience_entries >= 2:
        score += 10

    if sections.certifications:
        score += 10

    return min(100, score)