"""
Pydantic schemas for Document model.
"""
from typing import Optional
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    CV = "cv"
    COVER_LETTER = "cover_letter"
    CERTIFICATE = "certificate"
    TRANSCRIPT = "transcript"
    PORTFOLIO = "portfolio"
    JOB_DESCRIPTION = "job_description"
    OTHER = "other"


class DocumentBase(BaseModel):
    """Base schema for Document model."""
    document_type: DocumentType
    title: Optional[str] = None
    description: Optional[str] = None
    related_entity_type: Optional[str] = None  # cv, application, job, etc.
    related_entity_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: str  # pdf, docx, jpg, png, etc.
    file_size: int  # in bytes
    storage_path: Optional[str] = None  # Full storage path in blob/local storage
    uploaded_at: Optional[datetime] = None

    @field_validator("related_entity_id")
    def validate_related_entity_id(cls, v):
        """Validate related entity ID."""
        if v is not None and v <= 0:
            raise ValueError("Related entity ID must be a positive integer")
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
        if v and len(v) > 1000:
            raise ValueError("Description must be less than 1001 characters")
        return v

    @field_validator("related_entity_type")
    def validate_related_entity_type(cls, v):
        """Validate related entity type."""
        if v:
            allowed_types = ["cv", "application", "job", "interview", "follow_up", "profile", "other"]
            if v not in allowed_types:
                raise ValueError(f"Related entity type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator("file_name")
    def validate_file_name(cls, v):
        """Validate file name length."""
        if not v or len(v) > 255:
            raise ValueError("File name must be between 1 and 255 characters")
        return v

    @field_validator("file_path")
    def validate_file_path(cls, v):
        """Validate file path length."""
        if not v or len(v) > 500:
            raise ValueError("File path must be between 1 and 500 characters")
        return v

    @field_validator("file_type")
    def validate_file_type(cls, v):
        """Validate file type."""
        if not v or len(v) > 50:
            raise ValueError("File type must be between 1 and 50 characters")
        return v

    @field_validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size (max 100MB)."""
        if v <= 0 or v > 104857600:  # 100MB
            raise ValueError("File size must be between 1 byte and 100MB")
        return v

    @field_validator("storage_path")
    def validate_storage_path(cls, v):
        """Validate storage path length."""
        if v and len(v) > 500:
            raise ValueError("Storage path must be less than 501 characters")
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating a new Document."""
    document_type: DocumentType  # Required for creation
    file_name: str  # Required for creation
    file_path: str  # Required for creation
    file_type: str  # Required for creation
    file_size: int  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class DocumentUpdate(BaseModel):
    """Schema for updating a Document."""
    title: Optional[str] = None
    description: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None

    @field_validator("related_entity_id")
    def validate_related_entity_id(cls, v):
        """Validate related entity ID."""
        if v is not None and v <= 0:
            raise ValueError("Related entity ID must be a positive integer")
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
        if v and len(v) > 1000:
            raise ValueError("Description must be less than 1001 characters")
        return v

    @field_validator("related_entity_type")
    def validate_related_entity_type(cls, v):
        """Validate related entity type."""
        if v:
            allowed_types = ["cv", "application", "job", "interview", "follow_up", "profile", "other"]
            if v not in allowed_types:
                raise ValueError(f"Related entity type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator("file_name")
    def validate_file_name(cls, v):
        """Validate file name length."""
        if v and len(v) > 255:
            raise ValueError("File name must be less than 256 characters")
        return v

    @field_validator("file_path")
    def validate_file_path(cls, v):
        """Validate file path length."""
        if v and len(v) > 500:
            raise ValueError("File path must be less than 501 characters")
        return v

    @field_validator("file_type")
    def validate_file_type(cls, v):
        """Validate file type."""
        if v and len(v) > 50:
            raise ValueError("File type must be less than 51 characters")
        return v

    @field_validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size (max 100MB)."""
        if v is not None and (v <= 0 or v > 104857600):  # 100MB
            raise ValueError("File size must be between 1 byte and 100MB")
        return v

    @field_validator("storage_path")
    def validate_storage_path(cls, v):
        """Validate storage path length."""
        if v and len(v) > 500:
            raise ValueError("Storage path must be less than 501 characters")
        return v


class DocumentInDBBase(DocumentBase):
    """Base schema with ID for database operations."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    """Schema for returning Document data (response model)."""
    pass


# Alias for API endpoints
DocumentResponse = Document


class DocumentWithUser(DocumentInDBBase):
    """Schema for returning Document data with user information."""
    user: Optional['User'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for API endpoints
# ============================================================

class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    user_id: int


class DocumentListResponse(BaseModel):
    """Schema for document list response (lighter weight)."""
    id: int
    document_type: DocumentType
    title: Optional[str] = None
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
