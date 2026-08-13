"""
Pydantic schemas for CareerProfile model.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from datetime import datetime

if TYPE_CHECKING:
    from backend.schemas.user import User


class CareerProfileBase(BaseModel):
    """Base schema for CareerProfile model."""
    full_name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[List[Dict[str, Any]]] = None  # [{"institution": "...", "degree": "...", "year": "..."}]
    work_experience: Optional[List[Dict[str, Any]]] = None  # [{"company": "...", "position": "...", "years": "..."}]
    contact_info: Optional[Dict[str, Any]] = None  # {"phone": "...", "address": "...", "city": "...", "country": "..."}
    social_links: Optional[Dict[str, str]] = None  # {"linkedin": "...", "github": "...", "portfolio": "..."}

    @field_validator("full_name")
    def validate_full_name(cls, v):
        """Validate full name length."""
        if v and len(v) > 255:
            raise ValueError("Full name must be less than 256 characters")
        return v

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("summary")
    def validate_summary(cls, v):
        """Validate summary length."""
        if v and len(v) > 2000:
            raise ValueError("Summary must be less than 2001 characters")
        return v

    @field_validator("experience_years")
    def validate_experience_years(cls, v):
        """Validate experience years."""
        if v is not None and (v < 0 or v > 60):
            raise ValueError("Experience years must be between 0 and 60")
        return v

    @field_validator("skills")
    def validate_skills(cls, v):
        """Validate skills list."""
        if v:
            if len(v) > 50:
                raise ValueError("Maximum 50 skills allowed")
            for skill in v:
                if len(skill) > 50:
                    raise ValueError("Each skill must be less than 51 characters")
        return v


class CareerProfileCreate(CareerProfileBase):
    """Schema for creating a new CareerProfile."""
    user_id: int  # Required for creation

    @field_validator("user_id")
    def validate_user_id(cls, v):
        """Validate user ID."""
        if v <= 0:
            raise ValueError("User ID must be a positive integer")
        return v


class CareerProfileUpdate(BaseModel):
    """Schema for updating a CareerProfile."""
    full_name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    contact_info: Optional[Dict[str, Any]] = None
    social_links: Optional[Dict[str, str]] = None

    @field_validator("full_name")
    def validate_full_name(cls, v):
        """Validate full name length."""
        if v and len(v) > 255:
            raise ValueError("Full name must be less than 256 characters")
        return v

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("summary")
    def validate_summary(cls, v):
        """Validate summary length."""
        if v and len(v) > 2000:
            raise ValueError("Summary must be less than 2001 characters")
        return v

    @field_validator("experience_years")
    def validate_experience_years(cls, v):
        """Validate experience years."""
        if v is not None and (v < 0 or v > 60):
            raise ValueError("Experience years must be between 0 and 60")
        return v

    @field_validator("skills")
    def validate_skills(cls, v):
        """Validate skills list."""
        if v:
            if len(v) > 50:
                raise ValueError("Maximum 50 skills allowed")
            for skill in v:
                if len(skill) > 50:
                    raise ValueError("Each skill must be less than 51 characters")
        return v


class CareerProfileInDBBase(CareerProfileBase):
    """Base schema with ID for database operations."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CareerProfile(CareerProfileInDBBase):
    """Schema for returning CareerProfile data."""
    pass


class CareerProfileWithUser(CareerProfileInDBBase):
    """Schema for returning CareerProfile data with user information."""
    user: Optional['User'] = None

    class Config:
        from_attributes = True
