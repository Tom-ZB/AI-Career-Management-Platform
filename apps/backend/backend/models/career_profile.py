"""
Career Profile model for storing professional information.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class CareerProfile(Base):
    """Career profile model."""
    __tablename__ = "career_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Personal Information
    full_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)

    # Professional Details
    skills = Column(JSON, nullable=True)  # List of skills
    experience_years = Column(Integer, nullable=True)
    education = Column(JSON, nullable=True)  # List of education records
    work_experience = Column(JSON, nullable=True)  # List of work experience

    # Contact Information
    contact_info = Column(JSON, nullable=True)  # Phone, address, etc.
    social_links = Column(JSON, nullable=True)  # LinkedIn, GitHub, portfolio, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", backref="career_profile")
    cvs = relationship("CV", back_populates="career_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CareerProfile(id={self.id}, user_id={self.user_id}, full_name={self.full_name})>"
