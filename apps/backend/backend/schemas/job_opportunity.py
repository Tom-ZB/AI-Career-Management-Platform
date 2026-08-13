"""
Pydantic schemas for JobOpportunity model.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class JobType(str, Enum):
    """Job type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class JobOpportunityBase(BaseModel):
    """Base schema for JobOpportunity model."""
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    status: JobStatus = JobStatus.OPEN
    deadline: Optional[date] = None
    ai_keywords: Optional[List[str]] = None
    ai_summary: Optional[str] = None

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if not v or len(v) > 255:
            raise ValueError("Title must be between 1 and 255 characters")
        return v

    @field_validator("company")
    def validate_company(cls, v):
        """Validate company name length."""
        if v and len(v) > 255:
            raise ValueError("Company name must be less than 256 characters")
        return v

    @field_validator("location")
    def validate_location(cls, v):
        """Validate location length."""
        if v and len(v) > 255:
            raise ValueError("Location must be less than 256 characters")
        return v

    @field_validator("salary_min", "salary_max")
    def validate_salary(cls, v):
        """Validate salary values."""
        if v is not None and v < 0:
            raise ValueError("Salary must be a positive value")
        return v

    @field_validator("salary_currency")
    def validate_currency(cls, v):
        """Validate currency code."""
        if v and len(v) != 3:
            raise ValueError("Currency code must be 3 characters (e.g., USD, EUR)")
        return v.upper()

    @field_validator("description", "requirements", "responsibilities", "benefits")
    def validate_long_fields(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v

    @field_validator("source")
    def validate_source(cls, v):
        """Validate source length."""
        if v and len(v) > 255:
            raise ValueError("Source must be less than 256 characters")
        return v

    @field_validator("source_url")
    def validate_source_url(cls, v):
        """Validate source URL format."""
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

    @field_validator("ai_keywords")
    def validate_ai_keywords(cls, v):
        """Validate AI keywords."""
        if v:
            if len(v) > 100:
                raise ValueError("Maximum 100 AI keywords allowed")
            for keyword in v:
                if len(keyword) > 100:
                    raise ValueError("Each keyword must be less than 101 characters")
        return v

    @field_validator("ai_summary")
    def validate_ai_summary(cls, v):
        """Validate AI summary length."""
        if v and len(v) > 2000:
            raise ValueError("AI summary must be less than 2001 characters")
        return v


class JobOpportunityCreate(JobOpportunityBase):
    """Schema for creating a new JobOpportunity."""
    # All fields inherited from JobOpportunityBase
    # user_id is set by backend from current_user, not sent by client


class JobOpportunityUpdate(BaseModel):
    """Schema for updating a JobOpportunity."""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    status: Optional[JobStatus] = None
    deadline: Optional[date] = None
    ai_keywords: Optional[List[str]] = None
    ai_summary: Optional[str] = None

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("company")
    def validate_company(cls, v):
        """Validate company name length."""
        if v and len(v) > 255:
            raise ValueError("Company name must be less than 256 characters")
        return v

    @field_validator("location")
    def validate_location(cls, v):
        """Validate location length."""
        if v and len(v) > 255:
            raise ValueError("Location must be less than 256 characters")
        return v

    @field_validator("salary_min", "salary_max")
    def validate_salary(cls, v):
        """Validate salary values."""
        if v is not None and v < 0:
            raise ValueError("Salary must be a positive value")
        return v

    @field_validator("salary_currency")
    def validate_currency(cls, v):
        """Validate currency code."""
        if v and len(v) != 3:
            raise ValueError("Currency code must be 3 characters (e.g., USD, EUR)")
        return v.upper() if v else v

    @field_validator("description", "requirements", "responsibilities", "benefits")
    def validate_long_fields(cls, v):
        """Validate long text fields."""
        if v and len(v) > 5000:
            raise ValueError("Text fields must be less than 5001 characters")
        return v

    @field_validator("source")
    def validate_source(cls, v):
        """Validate source length."""
        if v and len(v) > 255:
            raise ValueError("Source must be less than 256 characters")
        return v

    @field_validator("source_url")
    def validate_source_url(cls, v):
        """Validate source URL format."""
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

    @field_validator("ai_keywords")
    def validate_ai_keywords(cls, v):
        """Validate AI keywords."""
        if v:
            if len(v) > 100:
                raise ValueError("Maximum 100 AI keywords allowed")
            for keyword in v:
                if len(keyword) > 100:
                    raise ValueError("Each keyword must be less than 101 characters")
        return v

    @field_validator("ai_summary")
    def validate_ai_summary(cls, v):
        """Validate AI summary length."""
        if v and len(v) > 2000:
            raise ValueError("AI summary must be less than 2001 characters")
        return v


class JobOpportunityInDBBase(JobOpportunityBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobOpportunity(JobOpportunityInDBBase):
    """Schema for returning JobOpportunity data (response model)."""
    pass


# Alias for API endpoints
JobOpportunityResponse = JobOpportunity


class JobOpportunityWithUser(JobOpportunityInDBBase):
    """Schema for returning JobOpportunity data with user information."""
    user: Optional['User'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class JobOpportunityListResponse(BaseModel):
    """Schema for job opportunity list response (lighter weight)."""
    id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: JobStatus
    created_at: datetime
    deadline: Optional[date] = None

    class Config:
        from_attributes = True
