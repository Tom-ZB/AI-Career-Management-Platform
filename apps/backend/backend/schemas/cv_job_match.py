"""
Pydantic schemas for CVJobMatch model.
"""
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from datetime import datetime

if TYPE_CHECKING:
    from backend.schemas.user import User
    from backend.schemas.cv import CV
    from backend.schemas.job_opportunity import JobOpportunity


class CVJobMatchBase(BaseModel):
    """Base schema for CVJobMatch model."""
    cv_id: int
    job_opportunity_id: int
    match_score: float  # 0-100
    match_details: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_recommendation: Optional[str] = None
    skills_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    keywords_match_score: Optional[float] = None

    @field_validator("cv_id", "job_opportunity_id")
    def validate_ids(cls, v):
        """Validate required IDs."""
        if v <= 0:
            raise ValueError("IDs must be positive integers")
        return v

    @field_validator("match_score")
    def validate_match_score(cls, v):
        """Validate match score."""
        if v < 0 or v > 100:
            raise ValueError("Match score must be between 0 and 100")
        return v

    @field_validator("skills_match_score", "experience_match_score", "education_match_score", "keywords_match_score")
    def validate_category_scores(cls, v):
        """Validate category scores."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Category scores must be between 0 and 100")
        return v

    @field_validator("ai_recommendation")
    def validate_ai_recommendation(cls, v):
        """Validate AI recommendation length."""
        if v and len(v) > 500:
            raise ValueError("AI recommendation must be less than 501 characters")
        return v


class CVJobMatchCreate(CVJobMatchBase):
    """Schema for creating a new CVJobMatch."""
    cv_id: int  # Required for creation
    job_opportunity_id: int  # Required for creation
    match_score: float  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class CVJobMatchUpdate(BaseModel):
    """Schema for updating a CVJobMatch."""
    match_score: Optional[float] = None
    match_details: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_recommendation: Optional[str] = None
    skills_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    keywords_match_score: Optional[float] = None

    @field_validator("match_score")
    def validate_match_score(cls, v):
        """Validate match score."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Match score must be between 0 and 100")
        return v

    @field_validator("skills_match_score", "experience_match_score", "education_match_score", "keywords_match_score")
    def validate_category_scores(cls, v):
        """Validate category scores."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Category scores must be between 0 and 100")
        return v

    @field_validator("ai_recommendation")
    def validate_ai_recommendation(cls, v):
        """Validate AI recommendation length."""
        if v and len(v) > 500:
            raise ValueError("AI recommendation must be less than 501 characters")
        return v


class CVJobMatchInDBBase(CVJobMatchBase):
    """Base schema with ID for database operations."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CVJobMatch(CVJobMatchInDBBase):
    """Schema for returning CVJobMatch data."""
    pass


class CVJobMatchWithDetails(CVJobMatchInDBBase):
    """Schema for returning CVJobMatch data with related details."""
    user: Optional['User'] = None
    cv: Optional['CV'] = None
    job_opportunity: Optional['JobOpportunity'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for AI Matching endpoints
# ============================================================

class MatchRequest(BaseModel):
    """Schema for CV-Job match request."""
    cv_id: int
    job_id: int


class MatchResponse(BaseModel):
    """Schema for CV-Job match response."""
    match_id: int
    cv_id: int
    job_id: int
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    keywords_score: float
    strengths: List[str] = []
    gaps: List[str] = []
    recommendation: str
    tips: List[str] = []
    details: Dict[str, Any] = {}


class CoverLetterRequest(BaseModel):
    """Schema for cover letter generation request."""
    cv_id: int
    job_id: int
    tone: Optional[str] = "professional"
    additional_notes: Optional[str] = None


class CoverLetterResponse(BaseModel):
    """Schema for cover letter generation response."""
    content: str
    cv_id: int
    job_id: int
    job_title: str
    company: str
    application_id: Optional[int] = None
