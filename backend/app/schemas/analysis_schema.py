"""
analysis_schema.py

Request schema for the resume analysis endpoint.
The response schema lives in scoring_schema.py (ResumeAnalysisResponse).
"""

from pydantic import BaseModel, field_validator
from typing import Optional


class ResumeAnalysisRequest(BaseModel):
    """
    Metadata submitted alongside the PDF upload.
    The PDF itself arrives as UploadFile in the route layer.
    """
    job_title: str
    company_name: Optional[str] = None
    job_description: Optional[str] = None

    @field_validator("job_title")
    @classmethod
    def job_title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("job_title must not be empty")
        return v

    @field_validator("company_name", "job_description", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v