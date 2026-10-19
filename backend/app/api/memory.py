from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import UserModel
from backend.app.auth.token import get_current_user
from backend.app.memory.user_preferences import UserPreferenceMemoryManager

router = APIRouter(prefix="/api/memory", tags=["User Preferences & Long-Term Memory"])

@router.get("")
def list_memories(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    memories = UserPreferenceMemoryManager.get_user_memories(user.id, db)
    return [
        {
            "memory_id": m.memory_id,
            "fact": m.fact,
            "memory_type": m.memory_type,
            "sensitivity": m.sensitivity,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in memories
    ]

@router.post("")
def add_memory(
    fact: str = Body(..., embed=True),
    consent: bool = Body(True, embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mem = UserPreferenceMemoryManager.save_memory(
        user_id=user.id,
        fact=fact,
        db=db,
        consent=consent
    )
    return {
        "status": "success",
        "memory": {
            "memory_id": mem.memory_id,
            "fact": mem.fact,
            "created_at": mem.created_at.isoformat()
        }
    }

@router.put("/{memory_id}")
def update_memory(
    memory_id: str,
    fact: str = Body(..., embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mem = UserPreferenceMemoryManager.update_memory(memory_id, user.id, fact, db)
    return {
        "status": "success",
        "memory": {
            "memory_id": mem.memory_id,
            "fact": mem.fact
        }
    }

@router.delete("/{memory_id}")
def delete_memory(
    memory_id: str,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    UserPreferenceMemoryManager.delete_memory(memory_id, user.id, db)
    return {"status": "success", "message": f"Memory {memory_id} deleted."}

@router.delete("")
def delete_all_memories(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = UserPreferenceMemoryManager.delete_all_memories(user.id, db)
    return {"status": "success", "deleted_count": count}

@router.post("/forget-conversation/{session_id}")
def forget_conversation(
    session_id: str,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    forgot = UserPreferenceMemoryManager.forget_conversation(session_id, user.id, db)
    return {"status": "success" if forgot else "not_found"}
