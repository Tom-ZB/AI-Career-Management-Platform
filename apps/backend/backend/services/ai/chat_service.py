"""
AI Chat Service - Handles chatbot conversations with context.
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config import settings
from backend.services.ai.llm_factory import LLMFactory
from backend.models.chat_message import ChatMessage, MessageRole
from backend.schemas.chat_message import ChatRequest, ChatResponse


# System prompt for the AI career assistant
SYSTEM_PROMPT = """You are an AI Career Assistant for the AI Career Management Platform.
You help users with:
- Career planning and advice
- CV/resume review and optimization
- Job search strategies
- Interview preparation
- Networking tips
- Career path planning

You can also perform actions on the user's data:
- Analyze their CV and provide feedback
- Match their CV to job descriptions
- Generate tailored cover letters
- Search and filter their job applications
- Provide analytics about their job search

Be professional, helpful, and concise. When you need to access the user's data,
tell them what action you'll perform and ask for confirmation if needed.

Current date: {current_date}
User: {user_name}"""


class AIChatService:
    """Service for AI chatbot conversations."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMFactory.get_llm()

    async def chat(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return AI response.

        Args:
            user_id: The authenticated user's ID
            request: Chat request with message and optional session_id

        Returns:
            ChatResponse with AI reply
        """
        session_id = request.session_id or f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Get conversation history
        history = self._get_conversation_history(user_id, session_id)

        # Build messages
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(
                current_date=datetime.utcnow().strftime("%Y-%m-%d"),
                user_name="User",  # TODO: Get actual user name
            ))
        ]

        # Add history (last 10 messages for context)
        for msg in history[-10:]:
            if msg.role == MessageRole.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                messages.append(AIMessage(content=msg.content))

        # Add current message
        messages.append(HumanMessage(content=request.message))

        # Get AI response
        start_time = datetime.utcnow()
        response = await self.llm.ainvoke(messages)
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Save messages to database
        self._save_message(user_id, session_id, MessageRole.USER, request.message)
        self._save_message(
            user_id, session_id, MessageRole.ASSISTANT,
            response.content, processing_time_ms=processing_time
        )

        return ChatResponse(
            message=response.content,
            session_id=session_id,
            processing_time_ms=processing_time,
            model_used=settings.LLM_PROVIDER,
        )

    def _get_conversation_history(self, user_id: int, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session."""
        return (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id,
            )
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def _save_message(
        self,
        user_id: int,
        session_id: str,
        role: MessageRole,
        content: str,
        processing_time_ms: Optional[int] = None,
    ):
        """Save a chat message to the database."""
        message = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            model_used=settings.LLM_PROVIDER,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(message)
        self.db.commit()