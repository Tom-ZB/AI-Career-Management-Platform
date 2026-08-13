"""
Pydantic schemas for Interview model.
"""
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from backend.schemas.user import User
    from backend.schemas.job_application import JobApplication


class InterviewType(str, Enum):
    """Interview type enumeration."""
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CASE_STUDY = "case_study"
    FINAL_ROUND = "final_round"


class InterviewStatus(str, Enum):
    """Interview status enumeration."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class InterviewBase(BaseModel):
    """Base schema for Interview model."""
    application_id: int
    interview_type: InterviewType
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = None
    interviewer_name: Optional[str] = None
    interviewer_title: Optional[str] = None
    interviewer_email: Optional[str] = None
    interviewer_phone: Optional[str] = None
    status: InterviewStatus = InterviewStatus.SCHEDULED
    rating: Optional[int] = None
    feedback: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("application_id")
    def validate_required_ids(cls, v):
        """Validate required IDs."""
        if v <= 0:
            raise ValueError("IDs must be positive integers")
        return v

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        """Validate description length."""
        if v and len(v) > 2000:
            raise ValueError("Description must be less than 2001 characters")
        return v

    @field_validator("location")
    def validate_location(cls, v):
        """Validate location length."""
        if v and len(v) > 500:
            raise ValueError("Location must be less than 501 characters")
        return v

    @field_validator("meeting_url")
    def validate_meeting_url(cls, v):
        """Validate meeting URL format."""
        if v:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:www\.)?'  # optional www.
                r'[a-zA-Z0-9.-]+'  # domain name
                r'\.[a-zA-Z]{2,}'  # top-level domain
                r'(?:/[^\s]*)?$'  # optional path
            )
            if not url_pattern.match(v):
                raise ValueError("Invalid URL format")
        return v

    @field_validator("scheduled_at")
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v and v < datetime.now():
            raise ValueError("Scheduled time must be in the future")
        return v

    @field_validator("duration_minutes")
    def validate_duration_minutes(cls, v):
        """Validate duration is reasonable."""
        if v is not None and (v <= 0 or v > 600):  # Max 10 hours
            raise ValueError("Duration must be between 1 and 600 minutes")
        return v

    @field_validator("interviewer_name")
    def validate_interviewer_name(cls, v):
        """Validate interviewer name length."""
        if v and len(v) > 255:
            raise ValueError("Interviewer name must be less than 256 characters")
        return v

    @field_validator("interviewer_title")
    def validate_interviewer_title(cls, v):
        """Validate interviewer title length."""
        if v and len(v) > 255:
            raise ValueError("Interviewer title must be less than 256 characters")
        return v

    @field_validator("interviewer_email")
    def validate_interviewer_email(cls, v):
        """Validate interviewer email format."""
        if v:
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("interviewer_phone")
    def validate_interviewer_phone(cls, v):
        """Validate interviewer phone number format."""
        if v and len(v) > 50:
            raise ValueError("Phone number must be less than 51 characters")
        return v

    @field_validator("rating")
    def validate_rating(cls, v):
        """Validate rating is between 1 and 5."""
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("feedback", "notes")
    def validate_long_text(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v


class InterviewCreate(InterviewBase):
    """Schema for creating a new Interview."""
    application_id: int  # Required for creation
    interview_type: InterviewType  # Required for creation
    scheduled_at: datetime  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class InterviewUpdate(BaseModel):
    """Schema for updating an Interview."""
    interview_type: Optional[InterviewType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    interviewer_name: Optional[str] = None
    interviewer_title: Optional[str] = None
    interviewer_email: Optional[str] = None
    interviewer_phone: Optional[str] = None
    status: Optional[InterviewStatus] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        """Validate description length."""
        if v and len(v) > 2000:
            raise ValueError("Description must be less than 2001 characters")
        return v

    @field_validator("location")
    def validate_location(cls, v):
        """Validate location length."""
        if v and len(v) > 500:
            raise ValueError("Location must be less than 501 characters")
        return v

    @field_validator("meeting_url")
    def validate_meeting_url(cls, v):
        """Validate meeting URL format."""
        if v:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:www\.)?'  # optional www.
                r'[a-zA-Z0-9.-]+'  # domain name
                r'\.[a-zA-Z]{2,}'  # top-level domain
                r'(?:/[^\s]*)?$'  # optional path
            )
            if not url_pattern.match(v):
                raise ValueError("Invalid URL format")
        return v

    @field_validator("scheduled_at")
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v and v < datetime.now():
            raise ValueError("Scheduled time must be in the future")
        return v

    @field_validator("duration_minutes")
    def validate_duration_minutes(cls, v):
        """Validate duration is reasonable."""
        if v is not None and (v <= 0 or v > 600):  # Max 10 hours
            raise ValueError("Duration must be between 1 and 600 minutes")
        return v

    @field_validator("interviewer_name")
    def validate_interviewer_name(cls, v):
        """Validate interviewer name length."""
        if v and len(v) > 255:
            raise ValueError("Interviewer name must be less than 256 characters")
        return v

    @field_validator("interviewer_title")
    def validate_interviewer_title(cls, v):
        """Validate interviewer title length."""
        if v and len(v) > 255:
            raise ValueError("Interviewer title must be less than 256 characters")
        return v

    @field_validator("interviewer_email")
    def validate_interviewer_email(cls, v):
        """Validate interviewer email format."""
        if v:
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("interviewer_phone")
    def validate_interviewer_phone(cls, v):
        """Validate interviewer phone number format."""
        if v and len(v) > 50:
            raise ValueError("Phone number must be less than 51 characters")
        return v

    @field_validator("rating")
    def validate_rating(cls, v):
        """Validate rating is between 1 and 5."""
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("feedback", "notes")
    def validate_long_text(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v


class InterviewInDBBase(InterviewBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Interview(InterviewInDBBase):
    """Schema for returning Interview data (response model)."""
    pass


# Alias for API endpoints
InterviewResponse = Interview


class InterviewWithDetails(InterviewInDBBase):
    """Schema for returning Interview data with related details."""
    user: Optional['User'] = None
    application: Optional['JobApplication'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class InterviewListResponse(BaseModel):
    """Schema for interview list response (lighter weight)."""
    id: int
    application_id: int
    interview_type: InterviewType
    title: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = None
    status: InterviewStatus
    created_at: datetime

    class Config:
        from_attributes = True
