"""
keyword_matcher.py

Responsibilities:
- Detect analyzer mode (job_title vs ats)
- Resolve job title → keyword set from title_keywords.py
- Extract keywords from a job description (ATS mode)
- Match resume text against a keyword set
- Return matched / missing keyword lists

All logic is deterministic. No ML, no embeddings, no external calls.
"""

import re
from typing import Optional
from backend.app.services.scoring.title_keywords import ROLE_KEYWORDS


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------

def detect_mode(job_description: Optional[str]) -> str:
    """
    Return 'ats' when a non-empty job description is provided, else 'job_title'.
    """
    if job_description and job_description.strip():
        return "ats"
    return "job_title"


# ---------------------------------------------------------------------------
# Title resolution
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase and collapse internal whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def resolve_title_to_role(job_title: str) -> Optional[str]:
    """
    Map a free-text job title to a canonical role key in ROLE_KEYWORDS.

    Strategy (in order):
    1. Exact match against canonical role names
    2. Exact match against known aliases
    3. Substring match — canonical role name appears in the title
    4. Substring match — any alias appears in the title
    Returns None if no match found.
    """
    normalized_title = _normalize(job_title)

    # Pass 1: exact canonical match
    if normalized_title in ROLE_KEYWORDS:
        return normalized_title

    # Pass 2: exact alias match
    for role, data in ROLE_KEYWORDS.items():
        if normalized_title in [_normalize(a) for a in data["aliases"]]:
            return role

    # Pass 3: canonical role name is substring of title
    for role in ROLE_KEYWORDS:
        if role in normalized_title:
            return role

    # Pass 4: any alias is substring of title
    for role, data in ROLE_KEYWORDS.items():
        for alias in data["aliases"]:
            if _normalize(alias) in normalized_title:
                return role

    return None


def get_keywords_for_role(role_key: str) -> list[str]:
    """
    Return a flat, deduplicated, lowercase keyword list for a resolved role key.
    Merges skills + technologies + concepts.
    """
    if role_key not in ROLE_KEYWORDS:
        return []
    data = ROLE_KEYWORDS[role_key]
    merged = data.get("skills", []) + data.get("technologies", []) + data.get("concepts", [])
    seen: set[str] = set()
    result: list[str] = []
    for kw in merged:
        normalized = _normalize(kw)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


# ---------------------------------------------------------------------------
# ATS keyword extraction from job description
# ---------------------------------------------------------------------------

# Stop words to exclude from extracted keywords
_STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "not", "no", "nor", "so",
    "yet", "both", "either", "each", "few", "more", "most", "other",
    "such", "than", "too", "very", "just", "we", "you", "our", "your",
    "their", "they", "this", "that", "these", "those", "it", "its",
    "as", "if", "about", "into", "through", "during", "including",
    "also", "must", "ability", "experience", "knowledge", "strong",
    "excellent", "good", "required", "preferred", "plus", "bonus",
    "looking", "seeking", "candidate", "candidates", "role", "position",
    "work", "working", "team", "join", "help", "using", "use",
    "build", "building", "develop", "developing", "like", "well",
    "need", "needs", "need.", "skills.", "plus.", "experience.",
    "familiarity", "familiar", "proficiency", "proficient", "proven",
})

# Multi-word tech terms to extract before single-word tokenization
_MULTI_WORD_TERMS: list[str] = [
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "reinforcement learning", "transfer learning",
    "data science", "data analysis", "data engineering", "data warehousing",
    "large language model", "large language models",
    "spring boot", "node.js", "next.js", "nuxt.js", "express.js",
    "react native", "vue.js", "angular.js",
    "continuous integration", "continuous deployment", "ci/cd",
    "infrastructure as code", "test driven development",
    "object oriented programming", "object-oriented programming",
    "aws sagemaker", "google cloud", "microsoft azure",
    "power bi", "google analytics", "github actions", "gitlab ci",
    "elk stack", "apache kafka", "apache spark",
    "progressive web app", "single page application",
    "version control", "agile methodology", "agile development",
    "unit testing", "integration testing", "end to end testing",
    "rest api", "restful api", "graphql api",
    "microservices architecture", "service oriented architecture",
]


def extract_keywords_from_jd(job_description: str) -> list[str]:
    """
    Extract a deduplicated keyword list from a raw job description.

    Strategy:
    1. Extract known multi-word tech terms first (preserves compound phrases)
    2. Tokenize remaining text into single words
    3. Filter out stop words and tokens shorter than 2 characters
    4. Deduplicate preserving first-occurrence order
    """
    text = _normalize(job_description)
    found: list[str] = []
    seen: set[str] = set()

    def _add(kw: str) -> None:
        if kw not in seen:
            seen.add(kw)
            found.append(kw)

    # Pass 1: multi-word terms
    for term in _MULTI_WORD_TERMS:
        if term in text:
            _add(term)
            # Blank out to prevent double-counting component words
            text = text.replace(term, " ")

    # Pass 2: single tokens — strip trailing punctuation before filtering
    tokens = re.findall(r"[a-z0-9][a-z0-9\.\+\#\-]*", text)
    for raw_token in tokens:
        token = raw_token.rstrip(".,;:!?)")
        if len(token) >= 2 and token not in _STOP_WORDS:
            _add(token)

    return found


# ---------------------------------------------------------------------------
# Resume keyword matching
# ---------------------------------------------------------------------------

def match_keywords(
    resume_text: str,
    keywords: list[str],
) -> tuple[list[str], list[str]]:
    """
    Given cleaned resume text and a list of target keywords, return:
        (matched_keywords, missing_keywords)

    Matching strategy:
    - Both resume text and keywords are lowercased
    - Each keyword is searched as a whole-word pattern in the resume text
      using word-boundary anchors (\b) where possible
    - Multi-word keywords use a simple substring match (boundaries implied by
      surrounding spaces/punctuation in natural text)
    """
    resume_lower = resume_text.lower()
    matched: list[str] = []
    missing: list[str] = []

    for kw in keywords:
        kw_lower = kw.lower()
        if " " in kw_lower:
            # Multi-word: substring match
            found = kw_lower in resume_lower
        else:
            # Single word: whole-word match to avoid false positives
            # e.g. "r" matching inside "react" or "render"
            pattern = r"\b" + re.escape(kw_lower) + r"\b"
            found = bool(re.search(pattern, resume_lower))

        if found:
            matched.append(kw)
        else:
            missing.append(kw)

    return matched, missing