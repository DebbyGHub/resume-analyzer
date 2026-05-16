from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from backend.app.schemas.scoring_schema import ResumeAnalysisResponse
from backend.app.services.analyzer.analyzer_service import run_analysis

router = APIRouter()


@router.post("/parse", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume PDF file"),
    job_title: str = Form(..., description="Target job title (required)"),
    company_name: Optional[str] = Form(None, description="Target company name (optional)"),
    job_description: Optional[str] = Form(None, description="Job description — activates ATS mode"),
):
    """
    Analyze a PDF resume.

    Pipeline (orchestrated by analyzer_service):
    1. Extract text from PDF
    2. Clean and normalize
    3. Detect sections
    4. Score (job_title mode or ATS mode)
    5. Generate rule-based feedback
    6. Return structured response with transparency metadata
    """
    return run_analysis(
        file=file,
        job_title=job_title.strip(),
        company_name=company_name.strip() if company_name else None,
        job_description=job_description.strip() if job_description else None,
    )