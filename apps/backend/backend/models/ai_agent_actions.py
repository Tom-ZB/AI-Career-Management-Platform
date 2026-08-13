"""
AI Agent Action model for tracking AI agent executions.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey, Float
from sqlalchemy.sql import func
from backend.database import Base
import enum


class ActionStatus(str, enum.Enum):
    """Action status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AIAgentAction(Base):
    """AI Agent action log model."""
    __tablename__ = "ai_agent_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(100), nullable=False)

    # Action Details
    action_type = Column(String(100), nullable=False)
    action_input = Column(JSON, nullable=True)
    action_output = Column(JSON, nullable=True)
    action_status = Column(Enum(ActionStatus), default=ActionStatus.PENDING, nullable=False)

    # Performance
    tokens_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<AIAgentAction(id={self.id}, type={self.action_type}, status={self.action_status})>"