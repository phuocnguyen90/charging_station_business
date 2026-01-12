from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User
from schemas.user import UserInDB, UserUpdate
from routers.v1.auth import get_db, get_current_user

router = APIRouter()

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

@router.get("/users", response_model=List[UserInDB])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role not in ["client", "installer", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user.role = role
    db.commit()
    db.refresh(user)
    return {"status": "success", "user_id": user.id, "new_role": user.role}
