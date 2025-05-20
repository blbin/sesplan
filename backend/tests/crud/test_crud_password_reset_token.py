import secrets
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from app.crud import crud_password_reset_token, crud_user
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User as UserModel
from app.schemas.user import UserCreate

# A simple helper to create a user for tests
def create_test_user(db: Session, email: str = "test@example.com", username: str = "testuser") -> UserModel:
    user_in = UserCreate(email=email, username=username, password="testpassword")
    return crud_user.create_user(db=db, user=user_in)


def test_create_password_reset_token(db_session: Session):
    user = create_test_user(db_session, email="create_token@example.com", username="createtokenuser")
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    db_token = crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=token_value, expires_at=expires_at
    )

    assert db_token is not None
    assert db_token.user_id == user.id
    assert db_token.token == token_value
    assert db_token.expires_at == expires_at
    
    retrieved_token = db_session.query(PasswordResetToken).filter(PasswordResetToken.id == db_token.id).first()
    assert retrieved_token is not None
    assert retrieved_token.token == token_value


def test_get_password_reset_token_by_token(db_session: Session):
    user = create_test_user(db_session, email="get_token@example.com", username="gettokenuser")
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    created_token = crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=token_value, expires_at=expires_at
    )

    retrieved_token = crud_password_reset_token.get_password_reset_token_by_token(db_session, token=token_value)
    assert retrieved_token is not None
    assert retrieved_token.id == created_token.id
    assert retrieved_token.token == token_value

    non_existent_token = crud_password_reset_token.get_password_reset_token_by_token(db_session, token="nonexistenttoken")
    assert non_existent_token is None


def test_get_active_password_reset_token_by_user(db_session: Session):
    user = create_test_user(db_session, email="active_token@example.com", username="activetokenuser")
    
    # Active token
    active_token_value = secrets.token_urlsafe(32)
    active_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=active_token_value, expires_at=active_expires_at
    )

    retrieved_active_token = crud_password_reset_token.get_active_password_reset_token_by_user(db_session, user_id=user.id)
    assert retrieved_active_token is not None
    assert retrieved_active_token.token == active_token_value

    # Expired token for the same user (after deleting previous ones to be sure)
    crud_password_reset_token.delete_all_password_reset_tokens_for_user(db_session, user_id=user.id)
    expired_token_value = secrets.token_urlsafe(32)
    expired_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=expired_token_value, expires_at=expired_expires_at
    )
    
    retrieved_expired_token = crud_password_reset_token.get_active_password_reset_token_by_user(db_session, user_id=user.id)
    assert retrieved_expired_token is None


def test_delete_password_reset_token(db_session: Session):
    user = create_test_user(db_session, email="delete_token@example.com", username="deletetokenuser")
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    db_token = crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=token_value, expires_at=expires_at
    )
    assert db_session.query(PasswordResetToken).filter(PasswordResetToken.id == db_token.id).first() is not None

    crud_password_reset_token.delete_password_reset_token(db_session, token_id=db_token.id)
    assert db_session.query(PasswordResetToken).filter(PasswordResetToken.id == db_token.id).first() is None


def test_delete_all_password_reset_tokens_for_user(db_session: Session):
    user = create_test_user(db_session, email="delete_all_tokens@example.com", username="deletealltokensuser")

    # Create multiple tokens for the user
    crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=secrets.token_urlsafe(32), expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    crud_password_reset_token.create_password_reset_token(
        db_session, user_id=user.id, token=secrets.token_urlsafe(32), expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    assert db_session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).count() == 2

    deleted_count = crud_password_reset_token.delete_all_password_reset_tokens_for_user(db_session, user_id=user.id)
    assert deleted_count == 2
    assert db_session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).count() == 0
