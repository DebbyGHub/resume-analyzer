"""
analyzer_service.py

Central orchestrator for the Rule-Based Resume Analyzer.

Responsibilities:
- Accept raw inputs (bytes, job_title, company_name, job_description)
- Run the full pipeline in order: clean → parse → score → feedback
- Collect parser warnings (non-fatal conditions)
- Assemble and return ResumeAnalysisResponse

The route layer (api/resume.py) is responsible only for:
- Receiving multipart form data
- Calling this service
- Returning the response

No business logic belongs in the route layer.
No parser or scorer knowledge belongs in the route layer.
"""

from typing import Optional
from fastapi import UploadFile

from backend.app.schemas.scoring_schema import (
    ResumeAnalysisResponse,
    FeedbackItem,
    ScoreResult,
)
from backend.app.schemas.resume_schema import DetectedSections, SectionCounts
from backend.app.services.parser.pdf_extractor import extract_text_from_upload
from backend.app.services.parser.text_cleaner import clean_text
from backend.app.services.parser.section_parser import parse_sections, compute_section_counts
from backend.app.services.scoring.score_calculator import calculate_score
from backend.app.services.scoring.feedback_generator import generate_feedback


def _collect_parser_warnings(
    sections: DetectedSections,
    counts: SectionCounts,
    raw_text: str,
) -> list[str]:
    """
    Non-fatal observations about the parsed resume.
    These inform the user without blocking the analysis.
    """
    warnings: list[str] = []

    detected_count = sum(
        1 for v in sections.model_dump().values() if v is not None
    )
    if detected_count == 0:
        warnings.append(
            "No standard section headings were detected. "
            "The parser used the full resume text for keyword matching."
        )

    if len(raw_text) < 200:
        warnings.append(
            "Extracted text is very short. "
            "The PDF may be partially image-based or have limited content."
        )

    if sections.experience and counts.experience_entries == 0:
        warnings.append(
            "Experience section found but no date ranges detected. "
            "Consider adding date ranges to each role."
        )

    return warnings


def run_analysis(
    file: UploadFile,
    job_title: str,
    company_name: Optional[str],
    job_description: Optional[str],
) -> ResumeAnalysisResponse:
    """
    Full analysis pipeline.

    Step 1 — Extract: PDF bytes → raw text
    Step 2 — Clean:   raw text → normalized text
    Step 3 — Parse:   normalized text → DetectedSections + SectionCounts
    Step 4 — Score:   sections + text → ScoreResult
    Step 5 — Feedback: scoring data → ranked feedback items
    Step 6 — Assemble: combine all outputs into ResumeAnalysisResponse
    """
    # Step 1 — Extract
    raw_text: str = extract_text_from_upload(file)

    # Step 2 — Clean
    cleaned_text: str = clean_text(raw_text)

    # Step 3 — Parse
    detected_sections: DetectedSections = parse_sections(cleaned_text)
    section_counts: SectionCounts = compute_section_counts(detected_sections)

    # Step 4 — Score
    score_result: ScoreResult = calculate_score(
        resume_text=cleaned_text,
        job_title=job_title,
        job_description=job_description,
        sections=detected_sections,
        counts=section_counts,
    )

    # Step 5 — Feedback
    raw_feedback = generate_feedback(
        sections=detected_sections,
        counts=section_counts,
        breakdown=score_result.score_breakdown,
        matched_keywords=score_result.matched_keywords,
        missing_keywords=score_result.missing_keywords,
        mode=score_result.mode,
    )
    feedback_items = [FeedbackItem(**item) for item in raw_feedback]

    # Step 6 — Warnings
    parser_warnings = _collect_parser_warnings(
        detected_sections, section_counts, cleaned_text
    )

    # Step 7 — Assemble
    return ResumeAnalysisResponse(
        job_title=job_title,
        company_name=company_name,
        mode=score_result.mode,
        total_score=score_result.total_score,
        score_breakdown=score_result.score_breakdown,
        matched_keywords=score_result.matched_keywords,
        missing_keywords=score_result.missing_keywords,
        feedback=feedback_items,
        detected_sections=detected_sections,
        section_counts=section_counts,
        raw_text=cleaned_text,
        parser_warnings=parser_warnings,
    )