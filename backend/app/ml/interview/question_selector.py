"""
question_selector.py

Resume-aware runtime interview question selector.

This module:
- selects interview questions ONLY from the curated dataset
- maps resume skills → dataset topics
- prioritises relevant technical domains
- balances difficulty levels
- prevents repetitive topic clustering

This module does NOT:
- generate questions
- evaluate semantic similarity
- use embeddings

Dataset source:
    ml/training/dataset_loader.py
"""

import random
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------

_ML_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
    .parent
    .parent
    / "ml"
)

if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from ml.training.dataset_loader import load_question_bank  # noqa: E402

# ---------------------------------------------------------------------------
# Skill → topic mapping
# ---------------------------------------------------------------------------

SKILL_TOPIC_MAP: dict[str, str] = {

    # Core CS
    "oop": "oop",
    "object oriented programming": "oop",

    "dbms": "dbms",
    "database": "dbms",

    "dsa": "dsa",
    "algorithms": "dsa",
    "data structures": "dsa",

    "operating systems": "operating_systems",
    "os": "operating_systems",

    "computer networks": "computer_networks",
    "networking": "computer_networks",

    # AI / ML
    "machine learning": "machine_learning",
    "ml": "machine_learning",
    "deep learning": "deep_learning",
    "nlp": "nlp",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "cnn": "cnn",
    "computer vision": "computer_vision",

    # Backend / APIs
    "api": "apis",
    "rest": "rest",
    "fastapi": "fastapi",
    "flask": "flask",
    "nodejs": "nodejs",
    "node.js": "nodejs",
    "express": "express",
    "jwt": "jwt",
    "oauth": "oauth",
    "websockets": "websockets",
    "redis": "redis",

    # Frontend
    "react": "react",
    "javascript": "javascript",
    "typescript": "typescript",
    "tailwind": "tailwind_css",
    "tailwind css": "tailwind_css",
    "html": "html",
    "css": "css",
    "web development": "web_development",

    # Languages
    "python": "python",
    "java": "java",
    "c": "c",
    "c++": "c++",
    "c#": "c#",
    "php": "php",
    "rust": "rust",
    "kotlin": "kotlin",

    # Databases
    "sql": "sql",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "mongodb": "mongodb",
    "sqlite": "sqlite",
    "oracle": "oracle",

    # DevOps / Deployment
    "docker": "docker",
    "git": "git",
    "github": "github",
    "linux": "linux",
    "deployment": "deployment",
    "vercel": "vercel",
    "render": "render",
    "postman": "postman",

    # Cloud
    "aws": "aws",
    "azure": "microsoft_azure",
    "microsoft azure": "microsoft_azure",
    "gcp": "gcp",
    "google cloud": "gcp",
    "firebase": "firebase",
    "supabase": "supabase",
    "cloud": "cloud_computing",
    "cloud computing": "cloud_computing",

    # Security
    "cybersecurity": "cybersecurity",

    # Data
    "json": "json",
}

# ---------------------------------------------------------------------------
# Difficulty balancing
# ---------------------------------------------------------------------------

_DIFFICULTY_ORDER = [
    "easy",
    "medium",
    "hard",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_questions() -> list[dict]:

    bank = load_question_bank()

    return list(bank.values())

# ---------------------------------------------------------------------------

def _resolve_topics(
    skills: list[str],
) -> list[str]:

    resolved: list[str] = []

    seen: set[str] = set()

    for skill in skills:

        topic = SKILL_TOPIC_MAP.get(
            skill.lower().strip()
        )

        if not topic:
            continue

        if topic in seen:
            continue

        resolved.append(topic)

        seen.add(topic)

    return resolved

# ---------------------------------------------------------------------------

def _group_by_difficulty(
    questions: list[dict],
) -> dict[str, list[dict]]:

    grouped = {
        "easy": [],
        "medium": [],
        "hard": [],
    }

    for q in questions:

        difficulty = q.get("difficulty", "medium")

        grouped.setdefault(difficulty, []).append(q)

    return grouped

# ---------------------------------------------------------------------------

def _balanced_skill_selection(
    questions: list[dict],
    limit: int,
) -> list[dict]:

    grouped = _group_by_difficulty(questions)

    for difficulty_questions in grouped.values():
        random.shuffle(difficulty_questions)

    selected: list[dict] = []

    # Try balanced selection:
    # easy → medium → hard cycling

    while len(selected) < limit:

        added = False

        for difficulty in _DIFFICULTY_ORDER:

            if grouped[difficulty]:

                selected.append(
                    grouped[difficulty].pop()
                )

                added = True

                if len(selected) >= limit:
                    break

        if not added:
            break

    return selected

# ---------------------------------------------------------------------------

def _fill_remaining_questions(
    selected: list[dict],
    all_questions: list[dict],
    limit: int,
) -> list[dict]:

    existing_ids = {
        q["id"]
        for q in selected
    }

    remaining = [
        q
        for q in all_questions
        if q["id"] not in existing_ids
    ]

    random.shuffle(remaining)

    needed = limit - len(selected)

    if needed > 0:
        selected.extend(remaining[:needed])

    return selected

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_interview_questions(
    skills: Optional[list[str]] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Select resume-aware interview questions.

    Args:
        skills:
            Resume skills extracted from resume analyzer.

        limit:
            Number of interview questions.

    Returns:
        List of question dicts.
    """

    limit = max(1, limit)

    all_questions = _load_questions()

    random.shuffle(all_questions)

    # -----------------------------------------------------------------------
    # No resume skills → generic balanced interview
    # -----------------------------------------------------------------------

    if not skills:

        return _balanced_skill_selection(
            all_questions,
            limit,
        )

    # -----------------------------------------------------------------------
    # Resume-aware selection
    # -----------------------------------------------------------------------

    matched_topics = _resolve_topics(skills)

    matched_questions = [
        q
        for q in all_questions
        if q.get("topic") in matched_topics
    ]

    # -----------------------------------------------------------------------
    # Balanced technical selection
    # -----------------------------------------------------------------------

    selected = _balanced_skill_selection(
        matched_questions,
        limit,
    )

    # -----------------------------------------------------------------------
    # Fill remaining slots
    # -----------------------------------------------------------------------

    selected = _fill_remaining_questions(
        selected,
        all_questions,
        limit,
    )

    return selected

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    example_skills = [
        "python",
        "react",
        "tensorflow",
        "docker",
        "aws",
    ]

    questions = select_interview_questions(
        skills=example_skills,
        limit=10,
    )

    print("\nSelected Questions:\n")

    for i, q in enumerate(questions, start=1):

        print(
            f"{i}. "
            f"[{q['topic']}] "
            f"[{q['difficulty']}] "
            f"{q['question']}"
        )