"""
Job Opportunity model for tracking job listings.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import enum


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class JobOpportunity(Base):
    """Job opportunity model."""
    __tablename__ = "job_opportunities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Job Details
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    job_type = Column(Enum(JobType), default=JobType.FULL_TIME, nullable=False)
    is_remote = Column(Integer, default=0, nullable=False)  # 0=False, 1=True

    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD", nullable=True)

    # Description
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)

    # Source Information
    source = Column(String(255), nullable=True)  # LinkedIn, Indeed, Company Website, etc.
    source_url = Column(String(500), nullable=True)

    # Status
    status = Column(Enum(JobStatus), default=JobStatus.OPEN, nullable=False)

    # Deadline
    deadline = Column(Date, nullable=True)

    # AI Analysis
    ai_keywords = Column(JSON, nullable=True)  # Extracted keywords from job description
    ai_summary = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    applications = relationship("JobApplication", back_populates="job_opportunity", cascade="all, delete-orphan")
    cv_job_matches = relationship("CVJobMatch", back_populates="job_opportunity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobOpportunity(id={self.id}, title={self.title}, company={self.company})>"
