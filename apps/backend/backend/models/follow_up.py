"""
Follow-up model for managing follow-up activities.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class FollowUpType(str, enum.Enum):
    """Follow-up type enumeration."""
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    MESSAGE = "message"
    MEETING = "meeting"
    THANK_YOU = "thank_you"
    FOLLOW_UP_EMAIL = "follow_up_email"
    NETWORKING = "networking"


class FollowUpStatus(str, enum.Enum):
    """Follow-up status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"


class FollowUp(Base):
    """Follow-up model."""
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(
        Integer,
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=True
    )
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True
    )

    # Follow-up Details
    follow_up_type = Column(Enum(FollowUpType), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=2, nullable=False)  # 1=Low, 2=Medium, 3=High

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(Enum(FollowUpStatus), default=FollowUpStatus.PENDING, nullable=False)

    # Contact Information
    contact_person = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    application = relationship("JobApplication", back_populates="follow_ups")
    interview = relationship("Interview", back_populates="follow_ups")

    def __repr__(self):
        return f"<FollowUp(id={self.id}, type={self.follow_up_type}, status={self.status})>"
