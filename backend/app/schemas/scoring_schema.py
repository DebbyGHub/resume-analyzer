from pydantic import BaseModel
from typing import Optional
from backend.app.schemas.resume_schema import DetectedSections, SectionCounts


class ScoreBreakdown(BaseModel):
    """
    Weighted score contributions per dimension.
    Each value is the sub-score × mode weight — contributions sum to total_score.
    """
    keyword_score:   int
    section_score:   int
    structure_score: int


class FeedbackItem(BaseModel):
    """A single rule-generated feedback item."""
    priority: str   # "high" | "medium" | "low"
    category: str   # "sections" | "keywords" | "structure"
    message:  str


class ScoreResult(BaseModel):
    """
    Internal output of the scoring pipeline.
    Does not include section bodies (those live in ResumeAnalysisResponse).
    """
    mode:             str   # "job_title" | "ats"
    total_score:      int   # 0–100
    score_breakdown:  ScoreBreakdown
    matched_keywords: list[str]
    missing_keywords: list[str]


class ResumeAnalysisResponse(BaseModel):
    """
    Complete API response — parser output + scoring + feedback.
    """
    # Request echo
    job_title:    str
    company_name: Optional[str] = None

    # Scoring
    mode:              str
    total_score:       int
    score_breakdown:   ScoreBreakdown
    matched_keywords:  list[str]
    missing_keywords:  list[str]
    extracted_skills: list[str]

    # Feedback
    feedback: list[FeedbackItem] = []

    # Parser output
    detected_sections: DetectedSections
    section_counts:    SectionCounts
    raw_text:          str

    # Transparency metadata
    parser_warnings: list[str] = []