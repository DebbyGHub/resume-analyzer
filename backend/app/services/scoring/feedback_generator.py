"""
feedback_generator.py

Generates deterministic, rule-based, priority-ranked feedback
from the parsed resume and scoring results.

Every feedback item is:
  - grounded in a concrete detected condition
  - categorised (sections | keywords | structure)
  - prioritised (high | medium | low)
  - actionable (tells the user what to do, not just what is wrong)

No AI. No LLMs. No randomness.
"""

from app.schemas.resume_schema import DetectedSections, SectionCounts
from app.schemas.scoring_schema import ScoreBreakdown


PRIORITY_HIGH   = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW    = "low"

CATEGORY_SECTIONS    = "sections"
CATEGORY_KEYWORDS    = "keywords"
CATEGORY_STRUCTURE   = "structure"


class FeedbackItem:
    __slots__ = ("priority", "category", "message")

    def __init__(self, priority: str, category: str, message: str) -> None:
        self.priority = priority
        self.category = category
        self.message  = message

    def to_dict(self) -> dict:
        return {
            "priority": self.priority,
            "category": self.category,
            "message":  self.message,
        }


_PRIORITY_ORDER = {PRIORITY_HIGH: 0, PRIORITY_MEDIUM: 1, PRIORITY_LOW: 2}


def generate_feedback(
    sections: DetectedSections,
    counts: SectionCounts,
    breakdown: ScoreBreakdown,
    matched_keywords: list[str],
    missing_keywords: list[str],
    mode: str,
) -> list[dict]:
    """
    Produce a sorted list of feedback dicts.

    Rules fire deterministically — the same input always produces the same output.
    Items are sorted: high → medium → low priority, then by category.
    """
    items: list[FeedbackItem] = []

    # ------------------------------------------------------------------ #
    # Section presence checks
    # ------------------------------------------------------------------ #

    if not sections.experience:
        items.append(FeedbackItem(
            PRIORITY_HIGH, CATEGORY_SECTIONS,
            "No work experience section detected. "
            "Add an 'Experience' or 'Work History' section listing your roles, "
            "responsibilities, and achievements."
        ))
    elif counts.experience_entries < 2:
        items.append(FeedbackItem(
            PRIORITY_MEDIUM, CATEGORY_SECTIONS,
            "Only one experience entry detected. "
            "Aim to include at least two roles or positions to demonstrate career progression."
        ))

    if not sections.education:
        items.append(FeedbackItem(
            PRIORITY_HIGH, CATEGORY_SECTIONS,
            "No education section detected. "
            "Add an 'Education' section with your degrees, institutions, and graduation years."
        ))

    if not sections.skills:
        items.append(FeedbackItem(
            PRIORITY_HIGH, CATEGORY_SECTIONS,
            "No skills section detected. "
            "Add a 'Skills' or 'Technical Skills' section listing relevant technologies "
            "and competencies."
        ))

    if not sections.summary:
        items.append(FeedbackItem(
            PRIORITY_MEDIUM, CATEGORY_SECTIONS,
            "No summary or objective statement detected. "
            "A 2–3 sentence professional summary at the top helps recruiters understand "
            "your value quickly."
        ))

    if not sections.projects:
        items.append(FeedbackItem(
            PRIORITY_MEDIUM, CATEGORY_SECTIONS,
            "No projects section detected. "
            "Adding personal or academic projects demonstrates initiative and "
            "applied technical skills."
        ))
    elif counts.project_entries == 1:
        items.append(FeedbackItem(
            PRIORITY_LOW, CATEGORY_SECTIONS,
            "Only one project detected. "
            "Including 2–3 projects gives a broader view of your technical range."
        ))

    if not sections.certifications:
        items.append(FeedbackItem(
            PRIORITY_LOW, CATEGORY_SECTIONS,
            "No certifications detected. "
            "Industry certifications (AWS, Google Cloud, etc.) can strengthen your profile "
            "for technical roles."
        ))

    # ------------------------------------------------------------------ #
    # Keyword coverage checks
    # ------------------------------------------------------------------ #

    total_keywords = len(matched_keywords) + len(missing_keywords)
    if total_keywords > 0:
        match_pct = len(matched_keywords) / total_keywords

        if mode == "ats":
            if match_pct < 0.40:
                items.append(FeedbackItem(
                    PRIORITY_HIGH, CATEGORY_KEYWORDS,
                    f"Low keyword match rate ({len(matched_keywords)}/{total_keywords} — "
                    f"{match_pct:.0%}). "
                    "Your resume is missing many keywords from the job description. "
                    "Review the missing keywords and incorporate relevant ones naturally."
                ))
            elif match_pct < 0.65:
                items.append(FeedbackItem(
                    PRIORITY_MEDIUM, CATEGORY_KEYWORDS,
                    f"Moderate keyword match ({len(matched_keywords)}/{total_keywords} — "
                    f"{match_pct:.0%}). "
                    "Incorporate more job-description keywords into your skills, "
                    "experience bullets, and summary."
                ))
            else:
                items.append(FeedbackItem(
                    PRIORITY_LOW, CATEGORY_KEYWORDS,
                    f"Good keyword coverage ({len(matched_keywords)}/{total_keywords} — "
                    f"{match_pct:.0%}). "
                    "Consider naturally including a few more missing keywords where applicable."
                ))
        else:
            # Job title mode — lighter keyword framing
            if match_pct < 0.35:
                items.append(FeedbackItem(
                    PRIORITY_MEDIUM, CATEGORY_KEYWORDS,
                    f"Low keyword alignment for this role "
                    f"({len(matched_keywords)}/{total_keywords} matched). "
                    "Review the expected skills for this job title and ensure your "
                    "resume reflects relevant technologies and concepts."
                ))
            elif match_pct >= 0.65:
                items.append(FeedbackItem(
                    PRIORITY_LOW, CATEGORY_KEYWORDS,
                    f"Strong keyword alignment for this role "
                    f"({len(matched_keywords)}/{total_keywords} matched)."
                ))

    # ------------------------------------------------------------------ #
    # Structure quality checks
    # ------------------------------------------------------------------ #

    if breakdown.structure_score < (20 * 0.4 if mode == "ats" else 30 * 0.4):
        items.append(FeedbackItem(
            PRIORITY_HIGH, CATEGORY_STRUCTURE,
            "Resume structure is weak. "
            "Ensure you have clearly labelled sections, at least one experience entry, "
            "an education entry, and a skills section."
        ))

    if sections.experience and counts.experience_entries == 0:
        items.append(FeedbackItem(
            PRIORITY_MEDIUM, CATEGORY_STRUCTURE,
            "An experience section was detected but no date ranges were found. "
            "Add date ranges (e.g. 'Jan 2021 – Dec 2023') to each role so "
            "your timeline is clear."
        ))

    # Skill completeness heuristic
    if sections.skills:
        skill_tokens = len([t for t in sections.skills.split() if len(t) >= 2])
        if skill_tokens < 5:
            items.append(FeedbackItem(
                PRIORITY_MEDIUM, CATEGORY_STRUCTURE,
                "Skills section appears sparse. "
                "List specific technologies, frameworks, and tools relevant to your target role."
            ))

    # ------------------------------------------------------------------ #
    # Sort: high → medium → low
    # ------------------------------------------------------------------ #

    items.sort(key=lambda x: _PRIORITY_ORDER[x.priority])
    return [item.to_dict() for item in items]