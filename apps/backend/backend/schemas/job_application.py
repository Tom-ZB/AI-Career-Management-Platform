"""
Pydantic schemas for JobApplication model.
"""
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from backend.schemas.user import User
    from backend.schemas.job_opportunity import JobOpportunity
    from backend.schemas.cv import CV


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    DRAFT = "draft"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplicationBase(BaseModel):
    """Base schema for JobApplication model."""
    job_opportunity_id: int
    cv_id: Optional[int] = None
    status: ApplicationStatus = ApplicationStatus.DRAFT
    application_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    cover_letter_content: Optional[str] = None
    cover_letter_file_path: Optional[str] = None
    notes: Optional[str] = None
    referral_source: Optional[str] = None

    @field_validator("job_opportunity_id")
    def validate_ids(cls, v):
        """Validate required IDs."""
        if v <= 0:
            raise ValueError("IDs must be positive integers")
        return v

    @field_validator("cv_id")
    def validate_cv_id(cls, v):
        """Validate CV ID."""
        if v is not None and v <= 0:
            raise ValueError("CV ID must be a positive integer")
        return v

    @field_validator("deadline")
    def validate_deadline(cls, v):
        """Validate deadline is in the future."""
        if v and v < datetime.now():
            raise ValueError("Deadline must be in the future")
        return v

    @field_validator("cover_letter_content")
    def validate_cover_letter_content(cls, v):
        """Validate cover letter content length."""
        if v and len(v) > 5000:
            raise ValueError("Cover letter content must be less than 5001 characters")
        return v

    @field_validator("cover_letter_file_path")
    def validate_cover_letter_file_path(cls, v):
        """Validate cover letter file path length."""
        if v and len(v) > 500:
            raise ValueError("Cover letter file path must be less than 501 characters")
        return v

    @field_validator("notes")
    def validate_notes(cls, v):
        """Validate notes length."""
        if v and len(v) > 2000:
            raise ValueError("Notes must be less than 2001 characters")
        return v

    @field_validator("referral_source")
    def validate_referral_source(cls, v):
        """Validate referral source length."""
        if v and len(v) > 255:
            raise ValueError("Referral source must be less than 256 characters")
        return v


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating a new JobApplication."""
    # user_id is set by the backend from current_user, not sent by client


class JobApplicationUpdate(BaseModel):
    """Schema for updating a JobApplication."""
    cv_id: Optional[int] = None
    status: Optional[ApplicationStatus] = None
    application_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    cover_letter_content: Optional[str] = None
    cover_letter_file_path: Optional[str] = None
    notes: Optional[str] = None
    referral_source: Optional[str] = None

    @field_validator("cv_id")
    def validate_cv_id(cls, v):
        """Validate CV ID."""
        if v is not None and v <= 0:
            raise ValueError("CV ID must be a positive integer")
        return v

    @field_validator("deadline")
    def validate_deadline(cls, v):
        """Validate deadline is in the future."""
        if v and v < datetime.now():
            raise ValueError("Deadline must be in the future")
        return v

    @field_validator("cover_letter_content")
    def validate_cover_letter_content(cls, v):
        """Validate cover letter content length."""
        if v and len(v) > 5000:
            raise ValueError("Cover letter content must be less than 5001 characters")
        return v

    @field_validator("cover_letter_file_path")
    def validate_cover_letter_file_path(cls, v):
        """Validate cover letter file path length."""
        if v and len(v) > 500:
            raise ValueError("Cover letter file path must be less than 501 characters")
        return v

    @field_validator("notes")
    def validate_notes(cls, v):
        """Validate notes length."""
        if v and len(v) > 2000:
            raise ValueError("Notes must be less than 2001 characters")
        return v

    @field_validator("referral_source")
    def validate_referral_source(cls, v):
        """Validate referral source length."""
        if v and len(v) > 255:
            raise ValueError("Referral source must be less than 256 characters")
        return v


class JobApplicationInDBBase(JobApplicationBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobApplication(JobApplicationInDBBase):
    """Schema for returning JobApplication data (response model)."""
    pass


# Alias for API endpoints
JobApplicationResponse = JobApplication


class JobApplicationWithDetails(JobApplicationInDBBase):
    """Schema for returning JobApplication data with related details."""
    user: Optional['User'] = None
    job_opportunity: Optional['JobOpportunity'] = None
    cv: Optional['CV'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class JobApplicationListResponse(BaseModel):
    """Schema for job application list response (lighter weight)."""
    id: int
    job_opportunity_id: int
    status: ApplicationStatus
    application_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
