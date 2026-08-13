"""
Interview model for managing interview schedules and feedback.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class InterviewType(str, enum.Enum):
    """Interview type enumeration."""
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CASE_STUDY = "case_study"
    FINAL_ROUND = "final_round"


class InterviewStatus(str, enum.Enum):
    """Interview status enumeration."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class Interview(Base):
    """Interview model."""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(
        Integer,
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False
    )

    # Interview Details
    interview_type = Column(Enum(InterviewType), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    meeting_url = Column(String(500), nullable=True)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)

    # Interviewer Information
    interviewer_name = Column(String(255), nullable=True)
    interviewer_title = Column(String(255), nullable=True)
    interviewer_email = Column(String(255), nullable=True)
    interviewer_phone = Column(String(50), nullable=True)

    # Status and Feedback
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    feedback = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    application = relationship("JobApplication", back_populates="interviews")
    follow_ups = relationship("FollowUp", back_populates="interview")

    def __repr__(self):
        return f"<Interview(id={self.id}, type={self.interview_type}, status={self.status})>"
