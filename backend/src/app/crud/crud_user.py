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


def update_password(db: Session, *, user: User, new_password_hash: str) -> User:
    """Update user's password."""
    user.password_hash = new_password_hash
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, *, email: str) -> User | None:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update a user."""
    # Ensure email is not part of the update_data if it's None or not set
    # as User model might have it as non-nullable.
    # However, UserUpdate schema might allow it to be optional.
    update_data = user_in.model_dump(exclude_unset=True)
    if 'email' in update_data and update_data['email'] is None:
        del update_data['email']

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user