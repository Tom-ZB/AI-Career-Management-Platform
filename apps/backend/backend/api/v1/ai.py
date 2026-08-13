"""
AI API endpoints - Chatbot, CV Analysis, Matching, Generation.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.chat_message import (
    ChatRequest, ChatResponse, ChatHistoryResponse,
)
from backend.schemas.cv import CVAnalysisResponse, CVGenerationRequest, CVGenerationResponse
from backend.schemas.cv_job_match import (
    MatchRequest, MatchResponse, CoverLetterRequest, CoverLetterResponse,
)

router = APIRouter()


# ============================================================
# AI Chatbot
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI chatbot."""
    # TODO: Implement AI chatbot with LangChain
    from backend.services.ai.chat_service import AIChatService
    service = AIChatService(db)
    return await service.chat(current_user.id, request)


@router.get("/chat/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat history."""
    from backend.models.chat_message import ChatMessage
    query = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    if session_id:
        query = query.filter(ChatMessage.session_id == session_id)
    messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()
    return messages[::-1]  # Return in chronological order


@router.get("/chat/sessions", response_model=List[dict])
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of chat sessions."""
    from backend.models.chat_message import ChatMessage
    from sqlalchemy import func, desc

    sessions = (
        db.query(
            ChatMessage.session_id,
            ChatMessage.conversation_title,
            func.max(ChatMessage.created_at).label('last_message_at')
        )
        .filter(ChatMessage.user_id == current_user.id)
        .group_by(ChatMessage.session_id, ChatMessage.conversation_title)
        .order_by(desc(func.max(ChatMessage.created_at)))
        .all()
    )

    return [
        {
            "session_id": s.session_id,
            "title": s.conversation_title or f"Conversation {s.session_id[:8]}",
            "last_message_at": s.last_message_at
        }
        for s in sessions
    ]


# ============================================================
# CV Analysis
# ============================================================

@router.post("/analyze-cv/{cv_id}", response_model=CVAnalysisResponse)
async def analyze_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze a CV with AI and provide feedback."""
    from backend.services.ai.cv_service import AICVService
    service = AICVService(db)
    return await service.analyze_cv(current_user.id, cv_id)


# ============================================================
# CV vs Job Description Matching
# ============================================================

@router.post("/match", response_model=MatchResponse)
async def match_cv_to_job(
    request: MatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Match a CV against a job description and get a score."""
    from backend.services.ai.matching_service import AIMatchingService
    service = AIMatchingService(db)
    return await service.match(current_user.id, request)


# ============================================================
# Tailored CV Generation
# ============================================================

@router.post("/generate-cv", response_model=CVGenerationResponse)
async def generate_tailored_cv(
    request: CVGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a tailored CV for a specific job."""
    from backend.services.ai.cv_service import AICVService
    service = AICVService(db)
    return await service.generate_tailored_cv(current_user.id, request)


# ============================================================
# Cover Letter Generation
# ============================================================

@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a tailored cover letter."""
    from backend.services.ai.cover_letter_service import AICoverLetterService
    service = AICoverLetterService(db)
    return await service.generate(current_user.id, request)


# ============================================================
# Natural Language Query
# ============================================================

@router.post("/query")
async def natural_language_query(
    query: str = Query(..., description="Natural language query about your career data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query your career data using natural language."""
    from backend.services.ai.query_service import AIQueryService
    service = AIQueryService(db)
    return await service.query(current_user.id, query)


# ============================================================
# Interview Preparation
# ============================================================

@router.post("/interview-prep/{interview_id}")
async def generate_interview_prep(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI-powered interview preparation materials."""
    from backend.services.ai.interview_service import AIInterviewService
    service = AIInterviewService(db)
    return await service.generate_prep(current_user.id, interview_id)


# ============================================================
# AI Agent Actions
# ============================================================

@router.post("/agent/action")
async def ai_agent_action(
    action_type: str = Query(..., description="Type of action to perform"),
    params: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute an AI agent action (query, analyze, generate, etc.)."""
    from backend.services.ai.agent_service import AIAgentService
    service = AIAgentService(db)
    return await service.execute_action(current_user.id, action_type, params)