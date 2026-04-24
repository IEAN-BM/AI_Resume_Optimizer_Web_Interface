# from pydantic import BaseModel, Field
# from typing import List, Optional

# class Resume(BaseModel):
#     content: str
#     skills: List[str]
#     experience_years: int

# class JobDescription(BaseModel):
#     content: str
#     requirements: List[str]

# class OptimizationResponse(BaseModel):
#     optimized_resume: str
#     match_score: float
#     suggestions: List[str]

#######################################
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ── Request models ────────────────────────────────────────────────────────────

class AnalyseRequest(BaseModel):
    resume_text: str
    job_description: str


class OptimizeRequest(BaseModel):
    resume_text: str
    job_description: str
    selected_skills: List[str] = []
    selected_keywords: List[str] = []
    selected_responsibilities: List[str] = []


class SaveRequest(BaseModel):
    optimized_resume: str
    category: str
    format: str = "pdf"   # "pdf" or "txt"


# ── Response models ───────────────────────────────────────────────────────────

class AnalyseResponse(BaseModel):
    job_title: str
    match_score: int
    match_summary: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    ats_keywords: List[str]
    responsibilities: List[str]
    candidate_matching_skills: List[str]
    candidate_missing_skills: List[str]


class OptimizeResponse(BaseModel):
    optimized_resume: str


class SaveResponse(BaseModel):
    id: str
    filename: str
    category: str
    format: str
    storage_path: str
    public_url: Optional[str]
    created_at: datetime


class ResumeListItem(BaseModel):
    id: str
    filename: str
    category: str
    format: str
    storage_path: str
    public_url: Optional[str]
    created_at: datetime


class ResumesResponse(BaseModel):
    total: int
    resumes: List[ResumeListItem]