"""
Schemas package initialization.
Convenience imports for all schemas.
"""
from backend.schemas.user import (
    Token, TokenPayload, PasswordUpdate,
    UserCreate, UserUpdate, User,
)
from backend.schemas.career_profile import (
    CareerProfileCreate, CareerProfileUpdate, CareerProfile,
)
from backend.schemas.cv import (
    CVCreate, CVUpdate, CV,
    CVListResponse, CVAnalysisResponse, CVGenerationRequest, CVGenerationResponse,
)
from backend.schemas.job_opportunity import (
    JobOpportunityCreate, JobOpportunityUpdate, JobOpportunity,
    JobOpportunityListResponse,
)
from backend.schemas.job_application import (
    JobApplicationCreate, JobApplicationUpdate, JobApplication,
    JobApplicationListResponse,
)
from backend.schemas.interview import (
    InterviewCreate, InterviewUpdate, Interview,
    InterviewListResponse,
)
from backend.schemas.follow_up import (
    FollowUpCreate, FollowUpUpdate, FollowUp,
    FollowUpListResponse,
)
from backend.schemas.document import (
    DocumentCreate, DocumentUpdate, Document,
    DocumentListResponse,
)
from backend.schemas.cv_job_match import (
    CVJobMatchCreate, CVJobMatchUpdate, CVJobMatch,
    MatchRequest, MatchResponse, CoverLetterRequest, CoverLetterResponse,
)
from backend.schemas.chat_message import (
    ChatMessageCreate, ChatMessageUpdate, ChatMessage,
    ChatRequest, ChatResponse, ChatHistoryResponse,
)

__all__ = [
    # User
    "Token", "TokenPayload", "PasswordUpdate",
    "UserCreate", "UserUpdate", "User",
    # Career Profile
    "CareerProfileCreate", "CareerProfileUpdate", "CareerProfile",
    # CV
    "CVCreate", "CVUpdate", "CV",
    "CVListResponse", "CVAnalysisResponse", "CVGenerationRequest", "CVGenerationResponse",
    # Job Opportunity
    "JobOpportunityCreate", "JobOpportunityUpdate", "JobOpportunity",
    "JobOpportunityListResponse",
    # Job Application
    "JobApplicationCreate", "JobApplicationUpdate", "JobApplication",
    "JobApplicationListResponse",
    # Interview
    "InterviewCreate", "InterviewUpdate", "Interview",
    "InterviewListResponse",
    # Follow-up
    "FollowUpCreate", "FollowUpUpdate", "FollowUp",
    "FollowUpListResponse",
    # Document
    "DocumentCreate", "DocumentUpdate", "Document",
    "DocumentListResponse",
    # CV-Job Match
    "CVJobMatchCreate", "CVJobMatchUpdate", "CVJobMatch",
    "MatchRequest", "MatchResponse", "CoverLetterRequest", "CoverLetterResponse",
    # Chat
    "ChatMessageCreate", "ChatMessageUpdate", "ChatMessage",
    "ChatRequest", "ChatResponse", "ChatHistoryResponse",
]