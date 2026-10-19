from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.db.models import ChatMessageModel, ChatSessionModel
from backend.app.config import settings

class ConversationMemoryManager:
    @staticmethod
    def get_recent_history(
        session_id: str,
        db: Session,
        max_turns: int = settings.short_term_memory_turns
    ) -> List[Dict[str, str]]:
        """
        Retrieves the most recent context-relevant message turns for a chat session.
        System instructions and retrieved RAG context always take priority over history.
        """
        messages = (
            db.query(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(max_turns * 2)
            .all()
        )

        messages.reverse()
        history: List[Dict[str, str]] = []
        for m in messages:
            history.append({
                "role": m.role,
                "content": m.content
            })
        return history

    @staticmethod
    def append_message(
        session_id: str,
        role: str,
        content: str,
        db: Session,
        language: str = "eng_Latn",
        sources: List[Dict[str, Any]] = None,
        follow_ups: List[str] = None
    ) -> ChatMessageModel:
        msg = ChatMessageModel(
            session_id=session_id,
            role=role,
            content=content,
            language=language,
            sources=sources or [],
            follow_up_suggestions=follow_ups or []
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
