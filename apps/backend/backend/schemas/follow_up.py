"""
Pydantic schemas for FollowUp model.
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum


class FollowUpType(str, Enum):
    """Follow-up type enumeration."""
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    MESSAGE = "message"
    MEETING = "meeting"
    THANK_YOU = "thank_you"
    FOLLOW_UP_EMAIL = "follow_up_email"
    NETWORKING = "networking"


class FollowUpStatus(str, Enum):
    """Follow-up status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"


class FollowUpBase(BaseModel):
    """Base schema for FollowUp model."""
    follow_up_type: FollowUpType
    title: Optional[str] = None
    description: Optional[str] = None
    priority: int = 2  # 1=Low, 2=Medium, 3=High
    scheduled_at: datetime
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    application_id: Optional[int] = None
    interview_id: Optional[int] = None
    status: FollowUpStatus = FollowUpStatus.PENDING
    completed_at: Optional[datetime] = None

    @field_validator("application_id", "interview_id")
    def validate_optional_ids(cls, v):
        """Validate optional IDs."""
        if v is not None and v <= 0:
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

    @field_validator("priority")
    def validate_priority(cls, v):
        """Validate priority is between 1 and 3."""
        if v < 1 or v > 3:
            raise ValueError("Priority must be between 1 and 3")
        return v

    @field_validator("scheduled_at")
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v < datetime.now():
            raise ValueError("Scheduled time must be in the future")
        return v

    @field_validator("contact_person")
    def validate_contact_person(cls, v):
        """Validate contact person length."""
        if v and len(v) > 255:
            raise ValueError("Contact person must be less than 256 characters")
        return v

    @field_validator("contact_email")
    def validate_contact_email(cls, v):
        """Validate contact email format."""
        if v:
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("contact_phone")
    def validate_contact_phone(cls, v):
        """Validate contact phone number format."""
        if v and len(v) > 50:
            raise ValueError("Phone number must be less than 51 characters")
        return v

    @field_validator("notes", "outcome")
    def validate_long_text(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v


class FollowUpCreate(FollowUpBase):
    """Schema for creating a new FollowUp."""
    follow_up_type: FollowUpType  # Required for creation
    scheduled_at: datetime  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class FollowUpUpdate(BaseModel):
    """Schema for updating a FollowUp."""
    follow_up_type: Optional[FollowUpType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    application_id: Optional[int] = None
    interview_id: Optional[int] = None
    status: Optional[FollowUpStatus] = None
    completed_at: Optional[datetime] = None

    @field_validator("application_id", "interview_id")
    def validate_optional_ids(cls, v):
        """Validate optional IDs."""
        if v is not None and v <= 0:
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

    @field_validator("priority")
    def validate_priority(cls, v):
        """Validate priority is between 1 and 3."""
        if v is not None and (v < 1 or v > 3):
            raise ValueError("Priority must be between 1 and 3")
        return v

    @field_validator("scheduled_at")
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future."""
        if v and v < datetime.now():
            raise ValueError("Scheduled time must be in the future")
        return v

    @field_validator("contact_person")
    def validate_contact_person(cls, v):
        """Validate contact person length."""
        if v and len(v) > 255:
            raise ValueError("Contact person must be less than 256 characters")
        return v

    @field_validator("contact_email")
    def validate_contact_email(cls, v):
        """Validate contact email format."""
        if v:
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("contact_phone")
    def validate_contact_phone(cls, v):
        """Validate contact phone number format."""
        if v and len(v) > 50:
            raise ValueError("Phone number must be less than 51 characters")
        return v

    @field_validator("notes", "outcome")
    def validate_long_text(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v


class FollowUpInDBBase(FollowUpBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FollowUp(FollowUpInDBBase):
    """Schema for returning FollowUp data (response model)."""
    pass


# Alias for API endpoints
FollowUpResponse = FollowUp


class FollowUpWithDetails(FollowUpInDBBase):
    """Schema for returning FollowUp data with related details."""
    user: Optional['User'] = None
    application: Optional['JobApplication'] = None
    interview: Optional['Interview'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class FollowUpListResponse(BaseModel):
    """Schema for follow-up list response (lighter weight)."""
    id: int
    follow_up_type: FollowUpType
    title: Optional[str] = None
    priority: int
    scheduled_at: datetime
    status: FollowUpStatus
    application_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
