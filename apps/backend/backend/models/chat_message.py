"""
Chat Message model for AI chatbot conversations.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base
import enum


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(Base):
    """Chat message model for AI conversations."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Session Management
    session_id = Column(String(100), nullable=False, index=True)
    conversation_title = Column(String(255), nullable=True)

    # Message Content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Metadata
    token_count = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session={self.session_id})>"
