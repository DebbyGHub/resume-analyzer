from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from backend.app.ml.evaluation.answer_quality import evaluate_answer

from typing import Optional

from backend.app.ml.interview.question_selector import (
    select_interview_questions,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class AnswerEvaluationRequest(BaseModel):
    ideal_answer:     str
    candidate_answer: str

    @field_validator("ideal_answer", "candidate_answer")
    @classmethod
    def must_not_be_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} must not be empty")
        return v.strip()


class AnswerEvaluationResponse(BaseModel):
    similarity_score: float
    confidence_score: float
    final_score:      float
    quality:          str
    flags:            list[str]



class InterviewStartRequest(BaseModel):
    skills: Optional[list[str]] = None
    limit: int = 10


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/evaluate-answer",
    response_model=AnswerEvaluationResponse,
    summary="Evaluate a candidate interview answer",
    description=(
        "Computes semantic similarity between the ideal and candidate answers, "
        "applies confidence penalties, and returns a structured quality assessment."
    ),
)
def evaluate_interview_answer(
    request: AnswerEvaluationRequest,
) -> AnswerEvaluationResponse:
    try:
        result = evaluate_answer(
            ideal_answer=request.ideal_answer,
            candidate_answer=request.candidate_answer,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {exc}",
        ) from exc

    return AnswerEvaluationResponse(**result)


@router.post(
    "/start-interview",
    summary="Start a resume-aware interview",
)
def start_interview(
    request: InterviewStartRequest,
):

    questions = select_interview_questions(
        skills=request.skills,
        limit=request.limit,
    )

    return {
        "skills_used": request.skills,
        "question_count": len(questions),
        "questions": questions,
    }