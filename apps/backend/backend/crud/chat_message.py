"""
CRUD operations for ChatMessage model.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.crud.base import CRUDBase
from backend.models.chat_message import ChatMessage
from backend.schemas.chat_message import ChatMessageCreate, ChatMessageUpdate


class CRUDChatMessage(CRUDBase[ChatMessage, ChatMessageCreate, ChatMessageUpdate]):
    """
    CRUD operations for ChatMessage model.
    """

    def get_by_session_id(self, db: Session, *, session_id: str) -> List[ChatMessage]:
        """
        Get all messages in a session.
        """
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def get_by_user_id(self, db: Session, *, user_id: int) -> List[ChatMessage]:
        """
        Get all messages for a user.
        """
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .all()
        )

    def get_sessions_by_user(self, db: Session, *, user_id: int) -> List[str]:
        """
        Get all unique session IDs for a user.
        """
        from sqlalchemy import func

        sessions = (
            db.query(ChatMessage.session_id)
            .filter(ChatMessage.user_id == user_id)
            .distinct()
            .all()
        )
        return [session[0] for session in sessions]

    def get_session_titles_by_user(self, db: Session, *, user_id: int) -> List[dict]:
        """
        Get session titles and metadata for a user.
        """
        from sqlalchemy import func

        # Get the latest message in each session to use as title if no title is set
        latest_messages = (
            db.query(
                ChatMessage.session_id,
                ChatMessage.conversation_title,
                func.max(ChatMessage.created_at).label('last_message_at')
            )
            .filter(ChatMessage.user_id == user_id)
            .group_by(ChatMessage.session_id, ChatMessage.conversation_title)
            .order_by(func.max(ChatMessage.created_at).desc())
            .all()
        )

        sessions = []
        for msg in latest_messages:
            session_info = {
                "session_id": msg.session_id,
                "title": msg.conversation_title or f"Conversation {msg.session_id[:8]}",
                "last_message_at": msg.last_message_at
            }
            sessions.append(session_info)

        return sessions

    def get_messages_by_role(self, db: Session, *, user_id: int, role: str) -> List[ChatMessage]:
        """
        Get all messages of a specific role for a user.
        """
        from backend.models.chat_message import MessageRole

        role_enum = MessageRole(role)
        return (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == user_id,
                ChatMessage.role == role_enum
            )
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def create(self, db: Session, *, obj_in: ChatMessageCreate) -> ChatMessage:
        """
        Create a new chat message.
        """
        db_obj = ChatMessage(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ChatMessage, obj_in: ChatMessageUpdate) -> ChatMessage:
        """
        Update a chat message.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_messages_with_filters(
        self,
        db: Session,
        *,
        user_id: int,
        session_id: Optional[str] = None,
        role: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatMessage]:
        """
        Get messages with various filters.
        """
        from backend.models.chat_message import MessageRole
        from sqlalchemy import func

        query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)

        if session_id:
            query = query.filter(ChatMessage.session_id == session_id)

        if role:
            query = query.filter(ChatMessage.role == MessageRole(role))

        if start_date:
            query = query.filter(ChatMessage.created_at >= start_date)

        if end_date:
            query = query.filter(ChatMessage.created_at <= end_date)

        return query.offset(skip).limit(limit).order_by(ChatMessage.created_at.asc()).all()

    def delete_session(self, db: Session, *, session_id: str) -> int:
        """
        Delete all messages in a session.
        """
        deleted_count = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        db.commit()
        return deleted_count

    def get_conversation_history(
        self,
        db: Session,
        *,
        session_id: str,
        max_messages: int = 20
    ) -> List[ChatMessage]:
        """
        Get recent conversation history for a session (limited by max_messages).
        """
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(max_messages)
            .all()[::-1]  # Reverse to get chronological order
        )

    def get_user_conversations_summary(self, db: Session, *, user_id: int) -> dict:
        """
        Get summary of user's conversations.
        """
        from sqlalchemy import func

        # Get total number of conversations (unique sessions)
        total_sessions = len(self.get_sessions_by_user(db, user_id=user_id))

        # Get total number of messages
        total_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .count()
        )

        # Get message count by role
        role_counts = {}
        for role in ["user", "assistant", "system"]:
            count = (
                db.query(ChatMessage)
                .filter(
                    ChatMessage.user_id == user_id,
                    ChatMessage.role == role
                )
                .count()
            )
            role_counts[role] = count

        # Get date range
        date_range = (
            db.query(
                func.min(ChatMessage.created_at),
                func.max(ChatMessage.created_at)
            )
            .filter(ChatMessage.user_id == user_id)
            .first()
        )

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "messages_by_role": role_counts,
            "date_range_start": date_range[0],
            "date_range_end": date_range[1]
        }

    def update_session_title(self, db: Session, *, session_id: str, title: str) -> None:
        """
        Update the title of a conversation session.
        """
        # Find the first message in the session and update its title
        first_message = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .first()
        )

        if first_message:
            # Update all messages in the session with the new title
            db.query(ChatMessage).filter(ChatMessage.session_id == session_id).update({
                ChatMessage.conversation_title: title
            })
            db.commit()


# Create chat message CRUD instance
chat_message = CRUDChatMessage(ChatMessage)
