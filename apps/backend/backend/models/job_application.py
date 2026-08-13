"""
Job Application model for tracking job applications.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration."""
    DRAFT = "draft"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplication(Base):
    """Job application model."""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_opportunity_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False
    )
    cv_id = Column(
        Integer,
        ForeignKey("cvs.id", ondelete="SET NULL"),
        nullable=True
    )

    # Application Details
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False)
    application_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Cover Letter
    cover_letter_content = Column(Text, nullable=True)
    cover_letter_file_path = Column(String(500), nullable=True)
    cover_letter_ai_generated = Column(Boolean, default=False, nullable=False, comment="Was cover letter AI-generated?")

    # Additional Information
    notes = Column(Text, nullable=True)
    referral_source = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    job_opportunity = relationship("JobOpportunity", back_populates="applications")
    cv = relationship("CV", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="application", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobApplication(id={self.id}, status={self.status})>"
