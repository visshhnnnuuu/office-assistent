import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import UserMemoryModel, UserModel, ChatSessionModel, ChatMessageModel
from backend.app.config import settings

FORBIDDEN_MEMORY_PATTERNS = [
    re.compile(r'\b(password|passwd|otp|pin|passcode|token|secret|private[_\s]key)\b', re.IGNORECASE),
    re.compile(r'\b(salary|ctc|compensation|payroll|bonus|performance[_\s]rating)\b', re.IGNORECASE),
    re.compile(r'\b(medical|diagnosis|prescription|disease|doctor|illness|health[_\s]record)\b', re.IGNORECASE),
    re.compile(r'\b(credit[_\s]card|cvv|bank[_\s]account|pan[_\s]card|aadhaar|ssn)\b', re.IGNORECASE),
]

class UserPreferenceMemoryManager:
    @staticmethod
    def validate_memory_safety(fact: str) -> None:
        """
        Validates that a proposed memory fact does not violate confidentiality,
        contain secrets, passwords, OTPs, financial compensation, or medical records.
        """
        for pattern in FORBIDDEN_MEMORY_PATTERNS:
            if pattern.search(fact):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot save memory: Contains confidential, credential, financial, or sensitive personal data."
                )

    @staticmethod
    def get_user_memories(user_id: str, db: Session) -> List[UserMemoryModel]:
        return db.query(UserMemoryModel).filter(UserMemoryModel.user_id == user_id).all()

    @staticmethod
    def save_memory(
        user_id: str,
        fact: str,
        db: Session,
        memory_type: str = "preference",
        consent: bool = True
    ) -> UserMemoryModel:
        if not consent:
            raise HTTPException(status_code=400, detail="Explicit user consent is mandatory to store memory.")

        UserPreferenceMemoryManager.validate_memory_safety(fact)

        # Check user memory limit
        count = db.query(UserMemoryModel).filter(UserMemoryModel.user_id == user_id).count()
        if count >= settings.max_memory_items_per_user:
            raise HTTPException(status_code=400, detail=f"Maximum memory capacity ({settings.max_memory_items_per_user} items) reached. Please delete older items.")

        memory = UserMemoryModel(
            user_id=user_id,
            memory_type=memory_type,
            fact=fact.strip(),
            consent=consent,
            sensitivity="low"
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def update_memory(memory_id: str, user_id: str, new_fact: str, db: Session) -> UserMemoryModel:
        UserPreferenceMemoryManager.validate_memory_safety(new_fact)
        memory = (
            db.query(UserMemoryModel)
            .filter(UserMemoryModel.memory_id == memory_id, UserMemoryModel.user_id == user_id)
            .first()
        )
        if not memory:
            raise HTTPException(status_code=404, detail="Memory item not found.")

        memory.fact = new_fact.strip()
        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def delete_memory(memory_id: str, user_id: str, db: Session) -> bool:
        memory = (
            db.query(UserMemoryModel)
            .filter(UserMemoryModel.memory_id == memory_id, UserMemoryModel.user_id == user_id)
            .first()
        )
        if not memory:
            raise HTTPException(status_code=404, detail="Memory item not found.")
        db.delete(memory)
        db.commit()
        return True

    @staticmethod
    def delete_all_memories(user_id: str, db: Session) -> int:
        deleted = db.query(UserMemoryModel).filter(UserMemoryModel.user_id == user_id).delete()
        db.commit()
        return deleted

    @staticmethod
    def forget_conversation(session_id: str, user_id: str, db: Session) -> bool:
        session = (
            db.query(ChatSessionModel)
            .filter(ChatSessionModel.id == session_id, ChatSessionModel.user_id == user_id)
            .first()
        )
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True
