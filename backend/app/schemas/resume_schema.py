from pydantic import BaseModel
from typing import Optional


class DetectedSections(BaseModel):
    summary: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None


class SectionCounts(BaseModel):
    experience_entries: int = 0
    project_entries: int = 0
    education_entries: int = 0
    certification_entries: int = 0