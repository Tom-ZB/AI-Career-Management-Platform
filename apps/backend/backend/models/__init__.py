"""
Models package initialization.
Import all models here to ensure they are registered with SQLAlchemy.
"""
from backend.models.user import User
from backend.models.career_profile import CareerProfile
from backend.models.cv import CV
from backend.models.job_opportunity import JobOpportunity, JobStatus, JobType
from backend.models.job_application import JobApplication, ApplicationStatus
from backend.models.interview import Interview, InterviewType, InterviewStatus
from backend.models.follow_up import FollowUp, FollowUpType, FollowUpStatus
from backend.models.document import Document, DocumentType
from backend.models.cv_job_match import CVJobMatch
from backend.models.chat_message import ChatMessage, MessageRole
from backend.models.ai_agent_actions import AIAgentAction, ActionStatus

__all__ = [
    "User",
    "CareerProfile",
    "CV",
    "JobOpportunity",
    "JobStatus",
    "JobType",
    "JobApplication",
    "ApplicationStatus",
    "Interview",
    "InterviewType",
    "InterviewStatus",
    "FollowUp",
    "FollowUpType",
    "FollowUpStatus",
    "Document",
    "DocumentType",
    "CVJobMatch",
    "ChatMessage",
    "MessageRole",
    "AIAgentAction",
    "ActionStatus",
]
