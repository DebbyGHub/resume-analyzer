"""
test_scoring.py

Tests for keyword matching, mode detection, title resolution, and score calculation.
All scores are deterministic — same input → same output, always.
"""

import pytest
from app.services.scoring.keyword_matcher import (
    detect_mode,
    resolve_title_to_role,
    get_keywords_for_role,
    extract_keywords_from_jd,
    match_keywords,
)
from app.services.scoring.section_scorer import score_sections, score_structure
from app.services.scoring.score_calculator import calculate_score
from app.schemas.resume_schema import DetectedSections, SectionCounts


# ──────────────────────────────────────────────────────────────
# Mode detection
# ──────────────────────────────────────────────────────────────

class TestDetectMode:
    def test_no_jd_returns_job_title(self):
        assert detect_mode(None) == "job_title"

    def test_empty_jd_returns_job_title(self):
        assert detect_mode("") == "job_title"
        assert detect_mode("   ") == "job_title"

    def test_jd_present_returns_ats(self):
        assert detect_mode("We need a Python developer.") == "ats"


# ──────────────────────────────────────────────────────────────
# Title resolution
# ──────────────────────────────────────────────────────────────

class TestResolveTitle:
    def test_exact_canonical_match(self):
        assert resolve_title_to_role("backend developer") == "backend developer"

    def test_case_insensitive(self):
        assert resolve_title_to_role("Backend Developer") == "backend developer"

    def test_alias_match(self):
        assert resolve_title_to_role("software engineer") == "backend developer"

    def test_partial_match_react_developer(self):
        result = resolve_title_to_role("Senior React Developer")
        assert result == "frontend developer"

    def test_ml_engineer_alias(self):
        assert resolve_title_to_role("ML Engineer") == "machine learning engineer"

    def test_unknown_title_returns_none(self):
        assert resolve_title_to_role("Astronaut Chief Navigator") is None

    def test_full_stack_match(self):
        result = resolve_title_to_role("Fullstack Engineer")
        assert result == "full stack developer"


# ──────────────────────────────────────────────────────────────
# Keyword retrieval
# ──────────────────────────────────────────────────────────────

class TestGetKeywordsForRole:
    def test_backend_keywords_not_empty(self):
        kws = get_keywords_for_role("backend developer")
        assert len(kws) > 10

    def test_all_lowercase(self):
        kws = get_keywords_for_role("backend developer")
        assert all(kw == kw.lower() for kw in kws)

    def test_no_duplicates(self):
        kws = get_keywords_for_role("backend developer")
        assert len(kws) == len(set(kws))

    def test_unknown_role_returns_empty(self):
        assert get_keywords_for_role("nonexistent role xyz") == []


# ──────────────────────────────────────────────────────────────
# ATS keyword extraction
# ──────────────────────────────────────────────────────────────

class TestExtractKeywordsFromJD:
    JD = (
        "We need a Python backend engineer with FastAPI and PostgreSQL. "
        "Experience with Docker, Redis, and CI/CD pipelines required. "
        "Machine learning knowledge is a plus."
    )

    def test_extracts_python(self):
        kws = extract_keywords_from_jd(self.JD)
        assert "python" in kws

    def test_extracts_fastapi(self):
        kws = extract_keywords_from_jd(self.JD)
        assert "fastapi" in kws

    def test_extracts_multiword_machine_learning(self):
        kws = extract_keywords_from_jd(self.JD)
        assert "machine learning" in kws

    def test_extracts_ci_cd(self):
        kws = extract_keywords_from_jd(self.JD)
        assert "ci/cd" in kws

    def test_no_stop_words(self):
        kws = extract_keywords_from_jd(self.JD)
        stop_words = {"we", "and", "with", "a", "is"}
        assert not any(sw in kws for sw in stop_words)

    def test_no_duplicates(self):
        kws = extract_keywords_from_jd(self.JD)
        assert len(kws) == len(set(kws))

    def test_empty_jd(self):
        assert extract_keywords_from_jd("") == []


# ──────────────────────────────────────────────────────────────
# Keyword matching
# ──────────────────────────────────────────────────────────────

class TestMatchKeywords:
    RESUME = "Experienced with Python, FastAPI, PostgreSQL, and Docker. Used Redis for caching."

    def test_matched_present_keywords(self):
        matched, missing = match_keywords(self.RESUME, ["python", "fastapi"])
        assert "python" in matched
        assert "fastapi" in matched

    def test_missing_absent_keywords(self):
        matched, missing = match_keywords(self.RESUME, ["tensorflow", "pytorch"])
        assert "tensorflow" in missing
        assert "pytorch" in missing

    def test_whole_word_match_prevents_false_positive(self):
        # "r" should not match inside "react", "render", etc.
        resume = "I use React and render components."
        matched, missing = match_keywords(resume, ["r"])
        assert "r" in missing  # "r" alone should not match

    def test_multiword_keyword_match(self):
        resume = "Experience with machine learning and deep learning."
        matched, _ = match_keywords(resume, ["machine learning"])
        assert "machine learning" in matched

    def test_empty_keywords(self):
        matched, missing = match_keywords(self.RESUME, [])
        assert matched == []
        assert missing == []

    def test_case_insensitive_matching(self):
        matched, _ = match_keywords("Expert in PYTHON and FastAPI", ["python", "fastapi"])
        assert "python" in matched
        assert "fastapi" in matched


# ──────────────────────────────────────────────────────────────
# Section and structure scoring
# ──────────────────────────────────────────────────────────────

FULL_SECTIONS = DetectedSections(
    summary="Experienced developer.",
    experience="Backend Engineer 2022-2024\nJunior Dev 2020-2021",
    education="B.Tech Computer Science 2020",
    projects="Project A 2023\nProject B 2022",
    skills="Python, FastAPI, Docker",
    certifications="AWS Certified 2023",
)
FULL_COUNTS = SectionCounts(
    experience_entries=2,
    project_entries=2,
    education_entries=1,
    certification_entries=1,
)

EMPTY_SECTIONS = DetectedSections()
EMPTY_COUNTS = SectionCounts()


class TestSectionScorer:
    def test_full_sections_high_score(self):
        from app.services.scoring.section_scorer import score_sections
        score = score_sections(FULL_SECTIONS, FULL_COUNTS)
        assert score >= 90

    def test_empty_sections_zero_score(self):
        from app.services.scoring.section_scorer import score_sections
        score = score_sections(EMPTY_SECTIONS, EMPTY_COUNTS)
        assert score == 0

    def test_score_bounded(self):
        from app.services.scoring.section_scorer import score_sections
        score = score_sections(FULL_SECTIONS, FULL_COUNTS)
        assert 0 <= score <= 100


class TestStructureScorer:
    def test_full_structure_high_score(self):
        from app.services.scoring.section_scorer import score_structure
        score = score_structure(FULL_SECTIONS, FULL_COUNTS)
        assert score >= 80

    def test_empty_structure_zero(self):
        from app.services.scoring.section_scorer import score_structure
        score = score_structure(EMPTY_SECTIONS, EMPTY_COUNTS)
        assert score == 0

    def test_score_bounded(self):
        from app.services.scoring.section_scorer import score_structure
        score = score_structure(FULL_SECTIONS, FULL_COUNTS)
        assert 0 <= score <= 100


# ──────────────────────────────────────────────────────────────
# Score calculator integration
# ──────────────────────────────────────────────────────────────

RESUME_TEXT = (
    "Python FastAPI PostgreSQL Docker Redis CI/CD microservices "
    "REST API SQLAlchemy Kubernetes. "
    "Experience: Backend Engineer 2022-2024. "
    "Education: B.Tech 2020. "
    "Skills: Python, Docker, Redis."
)


class TestCalculateScore:
    def test_job_title_mode_score_bounded(self):
        result = calculate_score(RESUME_TEXT, "Backend Developer", None, FULL_SECTIONS, FULL_COUNTS)
        assert result.mode == "job_title"
        assert 0 <= result.total_score <= 100

    def test_ats_mode_activated_by_jd(self):
        result = calculate_score(RESUME_TEXT, "Backend Developer", "Need Python and FastAPI.", FULL_SECTIONS, FULL_COUNTS)
        assert result.mode == "ats"

    def test_weights_sum_correctly(self):
        result = calculate_score(RESUME_TEXT, "Backend Developer", None, FULL_SECTIONS, FULL_COUNTS)
        bd = result.score_breakdown
        # Weighted contributions should sum to total (may differ by 1 due to rounding)
        contrib_sum = bd.keyword_score + bd.section_score + bd.structure_score
        assert abs(contrib_sum - result.total_score) <= 2

    def test_deterministic(self):
        """Same input must always produce same output."""
        r1 = calculate_score(RESUME_TEXT, "Backend Developer", None, FULL_SECTIONS, FULL_COUNTS)
        r2 = calculate_score(RESUME_TEXT, "Backend Developer", None, FULL_SECTIONS, FULL_COUNTS)
        assert r1.total_score == r2.total_score
        assert r1.matched_keywords == r2.matched_keywords

    def test_empty_resume_graceful(self):
        result = calculate_score("", "Backend Developer", None, EMPTY_SECTIONS, EMPTY_COUNTS)
        assert 0 <= result.total_score <= 100
        assert result.matched_keywords == []

    def test_ats_matched_present_in_resume(self):
        result = calculate_score(
            "We need Python and FastAPI",
            "Developer",
            "We need Python and FastAPI expertise",
            FULL_SECTIONS, FULL_COUNTS,
        )
        assert "python" in result.matched_keywords or "fastapi" in result.matched_keywords