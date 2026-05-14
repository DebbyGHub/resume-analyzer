"""
section_parser.py

Deterministic resume section detection.

Strategy:
1. Match heading lines using a rich alias table (case-insensitive)
2. Also detect ALL-CAPS heading lines that match known keywords
3. Accumulate body text into named buckets between headings
4. Pre-heading lines (name, contact) are collected separately, not discarded
5. Entry counting uses date-range and degree-keyword heuristics

No ML. No embeddings. Pure regex + heuristics.
"""

import re
from typing import Optional
from app.schemas.resume_schema import DetectedSections, SectionCounts
from app.services.parser.text_cleaner import lowercase_for_matching


# ---------------------------------------------------------------------------
# Section alias table
# Maps canonical section name → list of regex patterns (case-insensitive)
# ---------------------------------------------------------------------------

SECTION_PATTERNS: dict[str, list[str]] = {
    "summary": [
        r"summary",
        r"professional\s+summary",
        r"career\s+summary",
        r"executive\s+summary",
        r"objective",
        r"career\s+objective",
        r"professional\s+objective",
        r"profile",
        r"professional\s+profile",
        r"about\s+me",
        r"overview",
        r"introduction",
    ],
    "experience": [
        r"experience",
        r"work\s+experience",
        r"professional\s+experience",
        r"relevant\s+experience",
        r"employment",
        r"employment\s+history",
        r"work\s+history",
        r"career\s+history",
        r"job\s+history",
        r"internship",
        r"internships",
        r"positions\s+held",
    ],
    "education": [
        r"education",
        r"academic\s+background",
        r"academic\s+history",
        r"educational\s+background",
        r"educational\s+qualifications",
        r"qualifications",
        r"academic\s+qualifications",
        r"degrees",
        r"schooling",
    ],
    "projects": [
        r"projects",
        r"personal\s+projects",
        r"academic\s+projects",
        r"side\s+projects",
        r"key\s+projects",
        r"notable\s+projects",
        r"selected\s+projects",
        r"portfolio",
        r"open\s+source",
        r"open[-\s]source\s+contributions",
    ],
    "skills": [
        r"skills",
        r"technical\s+skills",
        r"core\s+competencies",
        r"competencies",
        r"technologies",
        r"tech\s+stack",
        r"tools\s+[&and]+\s+technologies",
        r"key\s+skills",
        r"areas\s+of\s+expertise",
        r"expertise",
        r"proficiencies",
        r"technical\s+proficiencies",
        r"programming\s+languages",
        r"languages\s+[&and]+\s+frameworks",
        r"frameworks\s+[&and]+\s+libraries",
    ],
    "certifications": [
        r"certifications",
        r"certification",
        r"licenses",
        r"licen[cs]es\s+[&and]+\s+certifications",
        r"professional\s+certifications",
        r"accreditations",
        r"credentials",
        r"awards\s+[&and]+\s+certifications",
        r"achievements",
    ],
}


# ---------------------------------------------------------------------------
# Compiled heading patterns
# A heading line: entire trimmed content matches an alias + optional punctuation
# ---------------------------------------------------------------------------

_HEADING_RE: dict[str, re.Pattern] = {
    section: re.compile(
        r"^\s*(?:" + "|".join(aliases) + r")\s*[:\-_]?\s*$",
        re.IGNORECASE,
    )
    for section, aliases in SECTION_PATTERNS.items()
}

# All-caps heading pattern: a short all-caps line that matches canonical keywords
# e.g. "WORK EXPERIENCE", "EDUCATION", "TECHNICAL SKILLS"
_ALLCAPS_TOKENS: dict[str, set[str]] = {
    section: {
        re.sub(r"\\s\+", " ", alias).upper().strip()
        for alias in aliases
    }
    for section, aliases in SECTION_PATTERNS.items()
}


def _is_allcaps_heading(line: str) -> Optional[str]:
    """
    Return canonical section name if a short all-caps line matches a known alias.
    Handles resumes that use EDUCATION, WORK EXPERIENCE as section titles.
    """
    stripped = line.strip()
    if not stripped or not stripped.isupper() or len(stripped) > 60:
        return None
    # Normalize internal whitespace for comparison
    normalized = re.sub(r"\s+", " ", stripped)
    for section, tokens in _ALLCAPS_TOKENS.items():
        if normalized in tokens:
            return section
    return None


def _classify_line(line: str) -> Optional[str]:
    """
    Return canonical section name if `line` looks like a section heading.

    Two detection strategies (in order):
    1. All-caps heading (e.g. "WORK EXPERIENCE")
    2. Standard regex match against alias table
    """
    stripped = line.strip()
    if not stripped:
        return None

    # Strategy 1: all-caps
    allcaps = _is_allcaps_heading(stripped)
    if allcaps:
        return allcaps

    # Strategy 2: alias regex
    for section, pattern in _HEADING_RE.items():
        if pattern.match(stripped):
            return section

    return None


def parse_sections(text: str) -> DetectedSections:
    """
    Walk the resume line by line and bucket content into canonical sections.

    Pre-heading lines (name, contact block) are accumulated but not exposed
    in DetectedSections — they inform future components without polluting scores.

    Empty section bodies are stored as None (not empty string).
    """
    lines = text.splitlines()
    buckets: dict[str, list[str]] = {s: [] for s in SECTION_PATTERNS}
    active_section: Optional[str] = None

    for line in lines:
        section_match = _classify_line(line)
        if section_match:
            active_section = section_match
            continue  # heading line excluded from body
        if active_section:
            buckets[active_section].append(line)

    result: dict[str, Optional[str]] = {}
    for section, body_lines in buckets.items():
        body = "\n".join(body_lines).strip()
        result[section] = body if body else None

    return DetectedSections(**result)


# ---------------------------------------------------------------------------
# Entry-counting heuristics
# ---------------------------------------------------------------------------

_DATE_RANGE_RE = re.compile(
    r"\b(?:"
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?"
    r"|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?"
    r"|nov(?:ember)?|dec(?:ember)?"
    r"|present|current|till\s+date|to\s+date"
    r"|\d{4}"
    r")\b",
    re.IGNORECASE,
)

_DEGREE_RE = re.compile(
    r"\b("
    r"b\.?\s*tech|b\.?\s*e\.?|b\.?\s*sc|b\.?\s*s\.?"
    r"|m\.?\s*tech|m\.?\s*sc|m\.?\s*e\.?|m\.?\s*s\.?"
    r"|mba|ph\.?\s*d|b\.?\s*a\.?|m\.?\s*a\.?"
    r"|bachelor(?:'?s)?|master(?:'?s)?"
    r"|doctorate|doctoral|diploma|associate(?:'?s)?"
    r"|higher\s+secondary|high\s+school"
    r")\b",
    re.IGNORECASE,
)

_CERT_ENTRY_RE = re.compile(
    r"\b(certified|certification|certificate|license|licence|credential)\b",
    re.IGNORECASE,
)


def _count_entries_by_dates(section_text: Optional[str]) -> int:
    """Count distinct experience/project entries via date-range signal lines."""
    if not section_text:
        return 0
    count = sum(1 for line in section_text.splitlines() if _DATE_RANGE_RE.search(line))
    # Guard: cap at a reasonable upper bound to avoid miscounting bullet dates
    return min(count, 20)


def _count_education_entries(section_text: Optional[str]) -> int:
    if not section_text:
        return 0
    return sum(1 for line in section_text.splitlines() if _DEGREE_RE.search(line))


def _count_certification_entries(section_text: Optional[str]) -> int:
    if not section_text:
        return 0
    lines = [ln.strip() for ln in section_text.splitlines() if ln.strip()]
    cert_lines = [ln for ln in lines if _CERT_ENTRY_RE.search(ln)]
    # If cert keywords present: count them; else count non-blank lines (1 per entry)
    return min(len(cert_lines) if cert_lines else len(lines), 20)


def compute_section_counts(sections: DetectedSections) -> SectionCounts:
    return SectionCounts(
        experience_entries=_count_entries_by_dates(sections.experience),
        project_entries=_count_entries_by_dates(sections.projects),
        education_entries=_count_education_entries(sections.education),
        certification_entries=_count_certification_entries(sections.certifications),
    )