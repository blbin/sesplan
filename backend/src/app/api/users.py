from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.crud.user import create_user
from app.db.session import get_db

router = APIRouter()

@router.post("/users/")
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    created_user = create_user(db=db, user=user)
    return {"id": created_user.id, "email": created_user.email, "username": created_user.username}
