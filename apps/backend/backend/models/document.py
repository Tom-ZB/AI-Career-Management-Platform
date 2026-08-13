"""
Document model for managing uploaded files.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base
import enum


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    CV = "cv"
    COVER_LETTER = "cover_letter"
    CERTIFICATE = "certificate"
    TRANSCRIPT = "transcript"
    PORTFOLIO = "portfolio"
    JOB_DESCRIPTION = "job_description"
    OTHER = "other"


class Document(Base):
    """Document model for file storage."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Document Metadata
    document_type = Column(Enum(DocumentType), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Related Entity (polymorphic relationship)
    related_entity_type = Column(String(50), nullable=True)  # cv, application, job, etc.
    related_entity_id = Column(Integer, nullable=True)

    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, jpg, png, etc.
    file_size = Column(Integer, nullable=False)  # in bytes
    storage_path = Column(String(500), nullable=True)  # Full storage path in blob/local storage

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, file_name={self.file_name})>"
