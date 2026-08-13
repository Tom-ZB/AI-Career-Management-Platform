"""
CV-Job Match model for tracking AI matching results.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class CVJobMatch(Base):
    """CV to Job matching results model."""
    __tablename__ = "cv_job_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cv_id = Column(Integer, ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)
    job_opportunity_id = Column(
        Integer,
        ForeignKey("job_opportunities.id", ondelete="CASCADE"),
        nullable=False
    )

    # Match Results
    match_score = Column(Float, nullable=False)  # 0-100
    match_details = Column(JSON, nullable=True)  # Detailed matching information
    ai_analysis = Column(JSON, nullable=True)  # AI analysis results
    ai_recommendation = Column(String(500), nullable=True)  # AI recommendation text

    # Matching Categories (breakdown)
    skills_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    education_match_score = Column(Float, nullable=True)
    keywords_match_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    cv = relationship("CV", back_populates="cv_job_matches")
    job_opportunity = relationship("JobOpportunity", back_populates="cv_job_matches")

    def __repr__(self):
        return f"<CVJobMatch(id={self.id}, score={self.match_score})>"
