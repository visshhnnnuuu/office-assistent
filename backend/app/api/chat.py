import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import UserModel, ChatSessionModel, ChatMessageModel
from backend.app.auth.token import get_current_user
from backend.app.multilingual.language_detector import LanguageDetector
from backend.app.web.router import QueryRouter
from backend.app.web.search_client import WebSearchClient
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.bm25 import BM25Okapi
from backend.app.rag.hybrid_retriever import HybridRetriever
from backend.app.services.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["Claude-like Chat & Real-Time Streaming"])

# Global in-memory search indexes shared across backend
_vector_store = VectorStore()
_bm25 = BM25Okapi()
_retriever = HybridRetriever(_vector_store, _bm25)

def get_hybrid_retriever() -> HybridRetriever:
    return _retriever

@router.get("/sessions")
def list_chat_sessions(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = (
        db.query(ChatSessionModel)
        .filter(ChatSessionModel.user_id == user.id)
        .order_by(ChatSessionModel.pinned.desc(), ChatSessionModel.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "title": s.title,
            "pinned": s.pinned,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "message_count": len(s.messages)
        }
        for s in sessions
    ]

@router.post("/sessions")
def create_session(
    title: str = Body("New Conversation", embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSessionModel(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title, "pinned": session.pinned}

@router.get("/sessions/{session_id}")
def get_session_history(
    session_id: str,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = (
        db.query(ChatSessionModel)
        .filter(ChatSessionModel.id == session_id, ChatSessionModel.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Conversation session not found.")

    return {
        "id": session.id,
        "title": session.title,
        "pinned": session.pinned,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "language": m.language,
                "sources": m.sources,
                "follow_up_suggestions": m.follow_up_suggestions,
                "feedback": m.feedback,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in session.messages
        ]
    }

@router.post("/sessions/{session_id}/pin")
def toggle_pin_session(
    session_id: str,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = (
        db.query(ChatSessionModel)
        .filter(ChatSessionModel.id == session_id, ChatSessionModel.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    session.pinned = not session.pinned
    db.commit()
    return {"status": "success", "pinned": session.pinned}

@router.post("/feedback")
def submit_feedback(
    message_id: str = Body(..., embed=True),
    feedback: str = Body(..., embed=True), # helpful, not_helpful, reported
    notes: Optional[str] = Body(None, embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(ChatMessageModel).filter(ChatMessageModel.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    msg.feedback = feedback
    msg.feedback_notes = notes
    db.commit()
    return {"status": "success", "feedback": feedback}

@router.post("/stream")
async def chat_stream_endpoint(
    request: Request,
    message: str = Body(..., embed=True),
    session_id: Optional[str] = Body(None, embed=True),
    language_override: Optional[str] = Body(None, embed=True),
    answer_depth: Optional[str] = Body(None, embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Core Server-Sent Events (SSE) streaming endpoint.
    Performs language detection, intent routing, RBAC retrieval, and structured response streaming.
    """
    # 1. Resolve or create chat session
    if not session_id:
        session = ChatSessionModel(user_id=user.id, title=message[:40] + "...")
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    else:
        session = db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id, ChatSessionModel.user_id == user.id).first()
        if not session:
            session = ChatSessionModel(id=session_id, user_id=user.id, title=message[:40] + "...")
            db.add(session)
            db.commit()
            db.refresh(session)

    # 2. Persist user message
    user_msg = ChatMessageModel(
        session_id=session_id,
        role="user",
        content=message
    )
    db.add(user_msg)
    db.commit()

    # 3. Detect Language and respect overrides
    detected = LanguageDetector.detect(message)
    target_language = language_override if language_override and language_override != "auto" else detected["language_id"]
    active_depth = answer_depth or user.answer_depth or "standard"

    # 4. Route Query
    route_decision = QueryRouter.route_query(message)
    is_software_mode = route_decision["is_software_mode"]
    allow_web = route_decision["allow_web"]

    # 5. Hybrid Retrieval with RBAC Pre-Filter
    retrieved_chunks = []
    if route_decision["target"] in {"internal_rag", "hybrid", "security_incident"}:
        retriever = get_hybrid_retriever()
        retrieved_chunks = retriever.retrieve(
            query=message,
            user_role=user.role,
            user_department=user.department,
            db=db,
            detected_language=target_language,
            top_k=6
        )

    # 6. Web Search if permitted
    web_sources = []
    if allow_web:
        web_sources = await WebSearchClient.search(message, max_results=2)

    # SSE Generator function
    async def event_generator():
        accumulated_content = []
        final_sources = []
        final_suggestions = []

        # Stream initial language acknowledgment
        yield f"event: detected_language\ndata: {json.dumps(detected)}\n\n"
        yield f"event: session_id\ndata: {json.dumps({'session_id': session_id})}\n\n"

        async for chunk in LLMService.stream_structured_answer(
            question=message,
            retrieved_chunks=retrieved_chunks,
            web_sources=web_sources,
            language=target_language,
            answer_depth=active_depth,
            is_software_expert_mode=is_software_mode,
            user_role=user.role
        ):
            chunk_type = chunk.get("type")
            if chunk_type == "status":
                yield f"event: status\ndata: {json.dumps({'message': chunk.get('message')})}\n\n"
            elif chunk_type == "content_delta":
                accumulated_content.append(chunk.get("delta", ""))
                yield f"event: delta\ndata: {json.dumps({'delta': chunk.get('delta')})}\n\n"
            elif chunk_type == "complete":
                final_sources = chunk.get("sources", [])
                final_suggestions = chunk.get("follow_up_suggestions", [])
                yield f"event: complete\ndata: {json.dumps({'sources': final_sources, 'follow_up_suggestions': final_suggestions})}\n\n"

        # Persist assistant response in DB
        assistant_content = "".join(accumulated_content)
        asst_msg = ChatMessageModel(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            language=target_language,
            sources=final_sources,
            follow_up_suggestions=final_suggestions
        )
        db.add(asst_msg)
        session.updated_at = asst_msg.created_at
        db.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
