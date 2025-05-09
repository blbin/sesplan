from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate


def get_user(db: Session, user_id: int):
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def get_users_by_ids(db: Session, user_ids: List[int]) -> List[User]:
    """Get multiple users by their IDs."""
    if not user_ids:
        return []
    return db.query(User).filter(User.id.in_(user_ids)).all()


def create_user(db: Session, user: UserCreate):
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update a user."""
    update_data = user_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user