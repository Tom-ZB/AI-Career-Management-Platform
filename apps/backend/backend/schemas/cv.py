"""
Pydantic schemas for CV model.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from datetime import datetime
import json
from backend.schemas.user import User


class CVBase(BaseModel):
    """Base schema for CV model."""
    career_profile_id: Optional[int] = None
    title: str
    version: Optional[str] = None
    description: Optional[str] = None
    is_master: bool = False
    is_public: bool = False
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    ai_parsed_data: Optional[Dict[str, Any]] = None
    ai_keywords: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    content_text: Optional[str] = None

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if not v or len(v) > 255:
            raise ValueError("Title must be between 1 and 255 characters")
        return v

    @field_validator("version")
    def validate_version(cls, v):
        """Validate version length."""
        if v and len(v) > 50:
            raise ValueError("Version must be less than 51 characters")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        """Validate description length."""
        if v and len(v) > 1000:
            raise ValueError("Description must be less than 1001 characters")
        return v

    @field_validator("file_type")
    def validate_file_type(cls, v):
        """Validate file type."""
        if not v:
            return v

        # Convert MIME type to extension (e.g., 'application/pdf' -> 'pdf')
        if '/' in v:
            mime_to_ext = {
                'application/pdf': 'pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/msword': 'doc',
                'text/plain': 'txt',
                'application/rtf': 'rtf',
                'application/vnd.oasis.opendocument.text': 'odt',
            }
            v = mime_to_ext.get(v, v.split('/')[-1].split('+')[0])

        if v not in ["pdf", "docx", "txt", "rtf", "odt"]:
            raise ValueError("File type must be one of: pdf, docx, txt, rtf, odt")
        return v

    @field_validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size (max 10MB)."""
        if v is not None and (v <= 0 or v > 10485760):  # 10MB
            raise ValueError("File size must be between 1 byte and 10MB")
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

    @field_validator("content_text")
    def validate_content_text(cls, v):
        """Validate content text length."""
        if v and len(v) > 100000:  # 100KB
            raise ValueError("Content text must be less than 100001 characters")
        return v


class CVCreate(CVBase):
    """Schema for creating a new CV."""
    title: str  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class CVUpdate(BaseModel):
    """Schema for updating a CV."""
    career_profile_id: Optional[int] = None
    title: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    is_master: Optional[bool] = None
    is_public: Optional[bool] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    ai_parsed_data: Optional[Dict[str, Any]] = None
    ai_keywords: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    content_text: Optional[str] = None

    @field_validator("title")
    def validate_title(cls, v):
        """Validate title length."""
        if v and len(v) > 255:
            raise ValueError("Title must be less than 256 characters")
        return v

    @field_validator("version")
    def validate_version(cls, v):
        """Validate version length."""
        if v and len(v) > 50:
            raise ValueError("Version must be less than 51 characters")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        """Validate description length."""
        if v and len(v) > 1000:
            raise ValueError("Description must be less than 1001 characters")
        return v

    @field_validator("file_type")
    def validate_file_type(cls, v):
        """Validate file type."""
        if not v:
            return v

        # Convert MIME type to extension (e.g., 'application/pdf' -> 'pdf')
        if '/' in v:
            mime_to_ext = {
                'application/pdf': 'pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/msword': 'doc',
                'text/plain': 'txt',
                'application/rtf': 'rtf',
                'application/vnd.oasis.opendocument.text': 'odt',
            }
            v = mime_to_ext.get(v, v.split('/')[-1].split('+')[0])

        if v not in ["pdf", "docx", "txt", "rtf", "odt"]:
            raise ValueError("File type must be one of: pdf, docx, txt, rtf, odt")
        return v

    @field_validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size (max 10MB)."""
        if v is not None and (v <= 0 or v > 10485760):  # 10MB
            raise ValueError("File size must be between 1 byte and 10MB")
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

    @field_validator("content_text")
    def validate_content_text(cls, v):
        """Validate content text length."""
        if v and len(v) > 100000:  # 100KB
            raise ValueError("Content text must be less than 100001 characters")
        return v


class CVInDBBase(CVBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CV(CVInDBBase):
    """Schema for returning CV data (response model)."""
    pass


# Alias for API endpoints that use "Response" naming convention
CVResponse = CV


class CVWithUser(CVInDBBase):
    """Schema for returning CV data with user information."""
    user: Optional['User'] = None
    career_profile: Optional['CareerProfile'] = None  # type: ignore

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class CVListResponse(BaseModel):
    """Schema for CV list response (lighter weight)."""
    id: int
    title: str
    version: Optional[str] = None
    is_master: bool = False
    is_ai_generated: bool = False
    file_name: Optional[str] = None
    ai_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CVAnalysisResponse(BaseModel):
    """Schema for CV analysis response."""
    cv_id: int
    overall_score: int
    dimensions: Dict[str, Any] = {}
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    keywords: List[str] = []

    class Config:
        from_attributes = True


class CVGenerationRequest(BaseModel):
    """Schema for CV generation request."""
    job_id: int
    profile_id: Optional[int] = None
    base_cv_id: Optional[int] = None
    additional_instructions: Optional[str] = None


class CVGenerationResponse(BaseModel):
    """Schema for CV generation response."""
    cv_id: int
    title: str
    content: Dict[str, Any]
    generated_for: Dict[str, Any]

    class Config:
        from_attributes = True
