"""
question_selector.py

Runtime interview question selection engine.

Selects a small, targeted interview set from the curated dataset.
This is NOT a generator — questions are always chosen from existing data.
This is NOT the semantic evaluator — it does not call USE or cosine similarity.

Depends on:
    ml/training/dataset_loader.py → load_question_bank()

Skill-to-topic mapping
----------------------
The dataset does not carry a "skills" field.
Skills are mapped to canonical dataset topics via SKILL_TOPIC_MAP.
When skills are provided, questions from matching topics are prioritised.
This map is the single place to extend as the dataset grows.
"""

import random
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path bootstrap — allow import from both backend and ml roots
# ---------------------------------------------------------------------------

_ML_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent / "ml"
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from ml.training.dataset_loader import load_question_bank  # noqa: E402

# ---------------------------------------------------------------------------
# Skill → topic mapping
# Keys are lowercase skill/technology names the frontend might send.
# Values are canonical topic strings from question_bank.json.
# ---------------------------------------------------------------------------

SKILL_TOPIC_MAP: dict[str, str] = {
    # OOP
    "java": "oop", "python": "oop", "c++": "oop", "c#": "oop",
    "object oriented": "oop", "oop": "oop", "design patterns": "oop",
    "inheritance": "oop", "polymorphism": "oop", "encapsulation": "oop",

    # DBMS
    "sql": "dbms", "mysql": "dbms", "postgresql": "dbms",
    "sqlite": "dbms", "database": "dbms", "dbms": "dbms",
    "nosql": "dbms", "mongodb": "dbms", "orm": "dbms",

    # DSA
    "data structures": "dsa", "algorithms": "dsa", "dsa": "dsa",
    "sorting": "dsa", "searching": "dsa", "trees": "dsa",
    "graphs": "dsa", "linked list": "dsa", "hash table": "dsa",

    # Operating Systems
    "os": "operating_systems", "operating systems": "operating_systems",
    "linux": "operating_systems", "processes": "operating_systems",
    "threads": "operating_systems", "concurrency": "operating_systems",
    "memory management": "operating_systems",

    # Computer Networks
    "networking": "computer_networks", "computer networks": "computer_networks",
    "tcp": "computer_networks", "http": "computer_networks",
    "dns": "computer_networks", "rest": "computer_networks",
    "api": "computer_networks",

    # Machine Learning
    "machine learning": "machine_learning", "ml": "machine_learning",
    "deep learning": "machine_learning", "tensorflow": "machine_learning",
    "pytorch": "machine_learning", "scikit-learn": "machine_learning",
    "neural networks": "machine_learning", "nlp": "machine_learning",
    "data science": "machine_learning",

    # Web Development
    "react": "web_development", "angular": "web_development",
    "vue": "web_development", "javascript": "web_development",
    "typescript": "web_development", "html": "web_development",
    "css": "web_development", "web development": "web_development",
    "frontend": "web_development", "backend": "web_development",
    "fastapi": "web_development", "flask": "web_development",
    "django": "web_development", "node": "web_development",

    # Java / Python
    "java collections": "java_python", "python decorators": "java_python",
    "garbage collection": "java_python", "multithreading": "java_python",
    "exceptions": "java_python", "java_python": "java_python",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_ALL_TOPICS = [
    "oop", "dbms", "dsa", "operating_systems",
    "computer_networks", "machine_learning", "web_development", "java_python",
]


def _load_questions() -> list[dict]:
    """Return all questions as flat dicts from the question bank."""
    bank = load_question_bank()
    return list(bank.values())


def _resolve_topics(skills: list[str]) -> list[str]:
    """Map skill strings to unique canonical topics."""
    topics: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        topic = SKILL_TOPIC_MAP.get(skill.lower().strip())
        if topic and topic not in seen:
            topics.append(topic)
            seen.add(topic)
    return topics


def _questions_for_topics(
    questions: list[dict],
    topics: list[str],
) -> list[dict]:
    """Return questions whose topic is in `topics`, preserving order."""
    topic_set = set(topics)
    return [q for q in questions if q.get("topic") in topic_set]


def _balanced_generic_set(questions: list[dict], limit: int) -> list[dict]:
    """
    Select a balanced set when no skills are provided.
    Picks one question per topic (cycling through topics) until limit is reached.
    """
    by_topic: dict[str, list[dict]] = {}
    for q in questions:
        topic = q.get("topic", "")
        by_topic.setdefault(topic, []).append(q)

    # Shuffle within each topic for variety between sessions
    for lst in by_topic.values():
        random.shuffle(lst)

    selected: list[dict] = []
    topic_iters = {t: iter(qs) for t, qs in by_topic.items()}
    active_topics = list(topic_iters.keys())

    while len(selected) < limit and active_topics:
        exhausted = []
        for topic in list(active_topics):
            if len(selected) >= limit:
                break
            try:
                selected.append(next(topic_iters[topic]))
            except StopIteration:
                exhausted.append(topic)
        for t in exhausted:
            active_topics.remove(t)

    return selected


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_interview_questions(
    skills: Optional[list[str]] = None,
    limit: int = 5,
) -> list[dict]:
    """
    Select an interview question set from the curated dataset.

    Args:
        skills: Optional list of skill/technology strings from the candidate's
                resume. Used to prioritise questions from matching topics.
                Example: ["python", "react", "sql"]
        limit:  Maximum number of questions to return. Defaults to 5.

    Returns:
        List of question dicts (id, topic, difficulty, question, ideal_answer).
        Length is at most `limit` and at most the total dataset size.

    Selection strategy:
        With skills:    Questions from skill-matched topics first.
                        Remaining slots filled from unmatched topics.
        Without skills: One question per topic, round-robin, shuffled.
    """
    limit = max(1, limit)
    all_questions = _load_questions()

    if not skills:
        return _balanced_generic_set(all_questions, limit)

    # ── Skill-targeted selection ──────────────────────────────────
    matched_topics = _resolve_topics(skills)
    matched_qs     = _questions_for_topics(all_questions, matched_topics)
    remaining_qs   = [q for q in all_questions if q not in matched_qs]

    # Shuffle both pools for session variety
    random.shuffle(matched_qs)
    random.shuffle(remaining_qs)

    # Fill from matched first, then pad with unmatched
    selected = matched_qs[:limit]
    if len(selected) < limit:
        selected += remaining_qs[: limit - len(selected)]

    return selected