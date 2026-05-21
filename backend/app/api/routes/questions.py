"""
questions.py

Serves interview questions to the frontend.

Architecture:
- Questions are loaded from the dataset loader.
- The response schema remains stable and production-ready.
- Only the underlying data source changes in future versions.

Mounted under /api/interview by main.py, so the final URL is:
  GET /api/interview/questions
"""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.ml.interview.question_selector import (
    select_interview_questions,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

Difficulty = Literal["easy", "medium", "hard"]


class InterviewQuestion(BaseModel):
    id: int
    topic: str
    difficulty: Difficulty
    question: str
    ideal_answer: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/questions",
    response_model=list[InterviewQuestion],
    summary="Get interview questions",
    description=(
        "Returns a targeted interview question set based on "
        "optional resume skills."
    ),
)
def get_questions(
    skills: str | None = None,
) -> list[InterviewQuestion]:

    parsed_skills = (
        [s.strip() for s in skills.split(",")]
        if skills
        else None
    )

    raw_questions = select_interview_questions(
        skills=parsed_skills,
        limit=5,
    )

    print("SKILLS RECEIVED:", parsed_skills)

    for q in raw_questions:
        print(q["topic"], "→", q["question"])

    return [
        InterviewQuestion(**question)
        for question in raw_questions
    ]