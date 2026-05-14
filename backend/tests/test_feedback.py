"""
test_feedback.py

Tests for the deterministic feedback generator.
"""

import pytest
from app.services.scoring.feedback_generator import generate_feedback
from app.schemas.resume_schema import DetectedSections, SectionCounts
from app.schemas.scoring_schema import ScoreBreakdown


FULL_SECTIONS = DetectedSections(
    summary="Experienced developer.",
    experience="Backend Engineer 2022-2024.",
    education="B.Tech 2020",
    projects="Resume AI 2024.",
    skills="Python, FastAPI, Docker",
    certifications="AWS 2023",
)
FULL_COUNTS = SectionCounts(experience_entries=2, project_entries=2, education_entries=1, certification_entries=1)

EMPTY_SECTIONS = DetectedSections()
EMPTY_COUNTS = SectionCounts()

GOOD_BREAKDOWN = ScoreBreakdown(keyword_score=25, section_score=38, structure_score=28)
WEAK_BREAKDOWN = ScoreBreakdown(keyword_score=5, section_score=8, structure_score=4)


class TestFeedbackStructure:
    def test_returns_list(self):
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python"], [], "job_title")
        assert isinstance(result, list)

    def test_each_item_has_required_keys(self):
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python"], [], "job_title")
        for item in result:
            assert "priority" in item
            assert "category" in item
            assert "message" in item

    def test_priority_values_valid(self):
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python"], [], "job_title")
        valid = {"high", "medium", "low"}
        assert all(item["priority"] in valid for item in result)

    def test_category_values_valid(self):
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python"], [], "job_title")
        valid = {"sections", "keywords", "structure"}
        assert all(item["category"] in valid for item in result)


class TestFeedbackPrioritySorting:
    def test_high_priority_before_low(self):
        result = generate_feedback(EMPTY_SECTIONS, EMPTY_COUNTS, WEAK_BREAKDOWN, [], ["python", "docker"], "ats")
        priorities = [item["priority"] for item in result]
        order = {"high": 0, "medium": 1, "low": 2}
        for i in range(len(priorities) - 1):
            assert order[priorities[i]] <= order[priorities[i + 1]]


class TestFeedbackMissingSections:
    def test_missing_experience_is_high_priority(self):
        sections = DetectedSections(education="B.Tech 2020", skills="Python")
        counts = SectionCounts()
        result = generate_feedback(sections, counts, GOOD_BREAKDOWN, [], [], "job_title")
        high_section = [i for i in result if i["priority"] == "high" and i["category"] == "sections"]
        assert any("experience" in i["message"].lower() for i in high_section)

    def test_missing_skills_is_high_priority(self):
        sections = DetectedSections(experience="Engineer 2022-2024", education="B.Tech")
        counts = SectionCounts(experience_entries=1)
        result = generate_feedback(sections, counts, GOOD_BREAKDOWN, [], [], "job_title")
        high_section = [i for i in result if i["priority"] == "high" and i["category"] == "sections"]
        assert any("skills" in i["message"].lower() for i in high_section)

    def test_full_sections_no_high_section_feedback(self):
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python"] * 20, [], "job_title")
        high_section = [i for i in result if i["priority"] == "high" and i["category"] == "sections"]
        assert len(high_section) == 0


class TestFeedbackKeywords:
    def test_low_ats_match_is_high_priority(self):
        missing = [f"kw{i}" for i in range(20)]
        matched = ["python"]
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, matched, missing, "ats")
        kw_items = [i for i in result if i["category"] == "keywords"]
        assert any(i["priority"] == "high" for i in kw_items)

    def test_high_ats_match_is_low_priority(self):
        matched = [f"kw{i}" for i in range(20)]
        result = generate_feedback(FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, matched, [], "ats")
        kw_items = [i for i in result if i["category"] == "keywords"]
        assert all(i["priority"] == "low" for i in kw_items)


class TestFeedbackDeterminism:
    def test_same_input_same_output(self):
        args = (FULL_SECTIONS, FULL_COUNTS, GOOD_BREAKDOWN, ["python", "docker"], ["tensorflow"], "job_title")
        r1 = generate_feedback(*args)
        r2 = generate_feedback(*args)
        assert r1 == r2

    def test_empty_input_no_crash(self):
        result = generate_feedback(EMPTY_SECTIONS, EMPTY_COUNTS, WEAK_BREAKDOWN, [], [], "job_title")
        assert isinstance(result, list)