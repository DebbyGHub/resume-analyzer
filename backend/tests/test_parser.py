"""
test_parser.py

Tests for text cleaning, section parsing, and section counting.
All tests are deterministic — same input always produces same output.
"""

from backend.app.services.parser.text_cleaner import (
    clean_text,
    remove_control_characters,
    normalize_unicode,
    normalize_bullet_lines,
    normalize_whitespace,
    collapse_blank_lines,
)
from backend.app.services.parser.section_parser import (
    parse_sections,
    compute_section_counts,
    _classify_line,
)


# ──────────────────────────────────────────────────────────────
# text_cleaner tests
# ──────────────────────────────────────────────────────────────

class TestRemoveControlCharacters:
    def test_removes_null_bytes(self):
        assert "\x00" not in remove_control_characters("hello\x00world")

    def test_removes_soft_hyphen(self):
        assert "\xad" not in remove_control_characters("soft\xadhyphen")

    def test_preserves_newlines(self):
        result = remove_control_characters("line1\nline2")
        assert "\n" in result

    def test_preserves_tabs(self):
        result = remove_control_characters("col1\tcol2")
        assert "\t" in result

    def test_empty_string(self):
        assert remove_control_characters("") == ""


class TestNormalizeUnicode:
    def test_expands_fi_ligature(self):
        assert normalize_unicode("\ufb01le") == "file"

    def test_expands_fl_ligature(self):
        assert normalize_unicode("\ufb02oor") == "floor"

    def test_converts_em_dash(self):
        assert normalize_unicode("2020\u20142022") == "2020-2022"

    def test_converts_smart_quotes(self):
        result = normalize_unicode("\u201chello\u201d")
        assert result == '"hello"'

    def test_converts_bullet(self):
        assert normalize_unicode("\u2022 item") == "- item"


class TestNormalizeBulletLines:
    def test_bullet_to_dash(self):
        result = normalize_bullet_lines("• Built APIs")
        assert result.startswith("- ")

    def test_asterisk_bullet(self):
        result = normalize_bullet_lines("* managed team")
        assert result.startswith("- ")

    def test_non_bullet_line_unchanged(self):
        result = normalize_bullet_lines("Regular sentence.")
        assert result == "Regular sentence."

    def test_multiline(self):
        text = "• First\n• Second\nNormal line"
        result = normalize_bullet_lines(text)
        lines = result.splitlines()
        assert lines[0].startswith("- ")
        assert lines[1].startswith("- ")
        assert lines[2] == "Normal line"


class TestNormalizeWhitespace:
    def test_collapses_spaces(self):
        result = normalize_whitespace("too    many   spaces")
        assert "  " not in result

    def test_preserves_newlines(self):
        result = normalize_whitespace("line1\nline2")
        assert "\n" in result

    def test_strips_line_edges(self):
        result = normalize_whitespace("  padded  ")
        assert result == "padded"


class TestCollapseBlankLines:
    def test_collapses_triple_blank_to_double(self):
        result = collapse_blank_lines("a\n\n\n\nb", max_consecutive=2)
        assert "\n\n\n" not in result

    def test_preserves_single_blank(self):
        result = collapse_blank_lines("a\n\nb")
        assert result == "a\n\nb"


class TestCleanTextPipeline:
    def test_full_pipeline_idempotent(self):
        """Cleaning already-clean text should not change it."""
        clean = "Summary\nExperienced engineer.\n\nExperience\nRole at Corp 2020-2022"
        result = clean_text(clean)
        assert result == clean

    def test_removes_noise(self):
        noisy = "hello\x00world\n\u2022 bullet\n\ufb01le"
        result = clean_text(noisy)
        assert "\x00" not in result
        assert "\u2022" not in result
        assert "\ufb01" not in result

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_only_whitespace(self):
        assert clean_text("   \n\n   ") == ""


# ──────────────────────────────────────────────────────────────
# section_parser tests
# ──────────────────────────────────────────────────────────────

SAMPLE_RESUME = """
John Doe
john@example.com | github.com/johndoe

Summary
Experienced backend developer with 4 years of experience.

Experience
Backend Engineer at Acme Corp (Jan 2022 - Present)
Built REST APIs using FastAPI and PostgreSQL.

Junior Developer at Startup Inc (Jun 2020 - Dec 2021)
Developed Python microservices.

Education
B.Tech in Computer Science, XYZ University, 2020

Projects
Resume AI Platform (Jan 2024 - Present)
Full-stack platform using React, FastAPI.

Smart Expense Tracker (Aug 2023 - Nov 2023)
Flask + SQLite tracker.

Skills
Python, FastAPI, PostgreSQL, Docker, Redis

Certifications
AWS Solutions Architect Associate - Amazon 2023
"""


class TestClassifyLine:
    def test_detects_experience(self):
        assert _classify_line("Experience") == "experience"

    def test_detects_work_history(self):
        assert _classify_line("Work History") == "experience"

    def test_detects_technical_skills(self):
        assert _classify_line("Technical Skills") == "skills"

    def test_detects_allcaps_education(self):
        assert _classify_line("EDUCATION") == "education"

    def test_detects_allcaps_experience(self):
        assert _classify_line("WORK EXPERIENCE") == "experience"

    def test_ignores_body_text(self):
        assert _classify_line("Built REST APIs using FastAPI") is None

    def test_ignores_empty_line(self):
        assert _classify_line("") is None

    def test_ignores_short_word(self):
        # "May" is a month, not a section heading
        assert _classify_line("May") is None

    def test_trailing_colon(self):
        assert _classify_line("Skills:") == "skills"

    def test_case_insensitive(self):
        assert _classify_line("CERTIFICATIONS") == "certifications"
        assert _classify_line("certifications") == "certifications"
        assert _classify_line("Certifications") == "certifications"


class TestParseSections:
    def setup_method(self):
        from backend.app.services.parser.text_cleaner import clean_text
        self.sections = parse_sections(clean_text(SAMPLE_RESUME))

    def test_detects_summary(self):
        assert self.sections.summary is not None
        assert "backend developer" in self.sections.summary.lower()

    def test_detects_experience(self):
        assert self.sections.experience is not None
        assert "fastapi" in self.sections.experience.lower()

    def test_detects_education(self):
        assert self.sections.education is not None
        assert "computer science" in self.sections.education.lower()

    def test_detects_projects(self):
        assert self.sections.projects is not None

    def test_detects_skills(self):
        assert self.sections.skills is not None
        assert "python" in self.sections.skills.lower()

    def test_detects_certifications(self):
        assert self.sections.certifications is not None

    def test_empty_text_returns_all_none(self):
        result = parse_sections("")
        for v in result.model_dump().values():
            assert v is None

    def test_headingless_resume_all_none(self):
        """A resume with no headings should parse to all-None sections."""
        plain = "John Doe\nSome text without any standard headings."
        result = parse_sections(plain)
        for v in result.model_dump().values():
            assert v is None


class TestSectionCounts:
    def setup_method(self):
        from backend.app.services.parser.text_cleaner import clean_text
        sections = parse_sections(clean_text(SAMPLE_RESUME))
        self.counts = compute_section_counts(sections)

    def test_experience_entries(self):
        assert self.counts.experience_entries >= 2

    def test_project_entries(self):
        assert self.counts.project_entries >= 2

    def test_education_entries(self):
        assert self.counts.education_entries >= 1

    def test_certification_entries(self):
        assert self.counts.certification_entries >= 1

    def test_none_sections_return_zero(self):
        from backend.app.schemas.resume_schema import DetectedSections
        empty_sections = DetectedSections()
        counts = compute_section_counts(empty_sections)
        assert counts.experience_entries == 0
        assert counts.project_entries == 0
        assert counts.education_entries == 0
        assert counts.certification_entries == 0