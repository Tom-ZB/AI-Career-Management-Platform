"""
Pydantic schemas for ChatMessage model.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage model."""
    session_id: str
    role: MessageRole
    content: str
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    conversation_title: Optional[str] = None

    @field_validator("session_id")
    def validate_session_id(cls, v):
        """Validate session ID length."""
        if not v or len(v) > 100:
            raise ValueError("Session ID must be between 1 and 100 characters")
        return v

    @field_validator("content")
    def validate_content(cls, v):
        """Validate content length."""
        if not v or len(v) > 100000:
            raise ValueError("Content must be between 1 and 100000 characters")
        return v

    @field_validator("conversation_title")
    def validate_conversation_title(cls, v):
        """Validate conversation title length."""
        if v and len(v) > 255:
            raise ValueError("Conversation title must be less than 256 characters")
        return v

    @field_validator("token_count")
    def validate_token_count(cls, v):
        """Validate token count."""
        if v is not None and v < 0:
            raise ValueError("Token count must be a positive integer")
        return v

    @field_validator("processing_time_ms")
    def validate_processing_time_ms(cls, v):
        """Validate processing time."""
        if v is not None and v < 0:
            raise ValueError("Processing time must be a positive integer")
        return v


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new ChatMessage."""
    session_id: str  # Required for creation
    role: MessageRole  # Required for creation
    content: str  # Required for creation
    # user_id is set by the backend from current_user, not sent by client


class ChatMessageUpdate(BaseModel):
    """Schema for updating a ChatMessage."""
    content: Optional[str] = None
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    conversation_title: Optional[str] = None

    @field_validator("content")
    def validate_content(cls, v):
        """Validate content length."""
        if v and len(v) > 100000:
            raise ValueError("Content must be less than 100001 characters")
        return v

    @field_validator("conversation_title")
    def validate_conversation_title(cls, v):
        """Validate conversation title length."""
        if v and len(v) > 255:
            raise ValueError("Conversation title must be less than 256 characters")
        return v

    @field_validator("token_count")
    def validate_token_count(cls, v):
        """Validate token count."""
        if v is not None and v < 0:
            raise ValueError("Token count must be a positive integer")
        return v

    @field_validator("processing_time_ms")
    def validate_processing_time_ms(cls, v):
        """Validate processing time."""
        if v is not None and v < 0:
            raise ValueError("Processing time must be a positive integer")
        return v


class ChatMessageInDBBase(ChatMessageBase):
    """Base schema with ID for database operations."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(ChatMessageInDBBase):
    """Schema for returning ChatMessage data."""
    pass


class ChatMessageWithUser(ChatMessageInDBBase):
    """Schema for returning ChatMessage data with user information."""
    user: Optional['User'] = None

    class Config:
        from_attributes = True


# ============================================================
# Additional schemas for AI Chat endpoints
# ============================================================

class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    @field_validator("message")
    def validate_message(cls, v):
        """Validate message."""
        if not v or len(v) > 10000:
            raise ValueError("Message must be between 1 and 10000 characters")
        return v


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    session_id: str
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""
    id: int
    session_id: str
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
