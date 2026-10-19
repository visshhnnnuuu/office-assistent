from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import UserModel
from backend.app.auth.token import get_current_user, create_access_token
from backend.app.auth.rbac import ALL_ROLES

router = APIRouter(prefix="/api/auth", tags=["Authentication & RBAC"])

@router.get("/me")
def get_user_profile(user: UserModel = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "department": user.department,
        "preferred_language": user.preferred_language,
        "answer_depth": user.answer_depth,
        "available_roles": ALL_ROLES
    }

@router.post("/switch-role")
def switch_user_role(
    role: str = Body(..., embed=True),
    department: str = Body("All", embed=True),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_clean = role.lower()
    if role_clean not in ALL_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {ALL_ROLES}")

    user.role = role_clean
    user.department = department
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role, "email": user.email})
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "department": user.department
        },
        "token": token
    }
