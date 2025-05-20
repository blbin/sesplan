from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from app.models.password_reset_token import PasswordResetToken

def create_password_reset_token(db: Session, *, user_id: int, token: str, expires_at: datetime) -> PasswordResetToken:
    """
    Creates a new password reset token.
    """
    db_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_password_reset_token_by_token(db: Session, *, token: str) -> PasswordResetToken | None:
    """
    Retrieves a password reset token by the token string.
    """
    return db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

def get_active_password_reset_token_by_user(db: Session, *, user_id: int) -> PasswordResetToken | None:
    """
    Retrieves an active (non-expired) password reset token for a user.
    """
    # Ensure expires_at is compared against a timezone-aware UTC datetime
    # The model stores expires_at as DateTime(timezone=True)
    # We assume that 'expires_at' is stored in UTC or is offset-aware.
    # datetime.now(timezone.utc) is a timezone-aware datetime object representing current UTC time.
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.expires_at > datetime.now(timezone.utc)
    ).first()

def delete_password_reset_token(db: Session, *, token_id: int) -> None:
    """
    Deletes a password reset token by its ID.
    """
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.id == token_id).first()
    if db_token:
        db.delete(db_token)
        db.commit()

def delete_all_password_reset_tokens_for_user(db: Session, *, user_id: int) -> int:
    """
    Deletes all password reset tokens for a specific user and returns the count of deleted tokens.
    """
    num_deleted = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).delete()
    db.commit()
    return num_deleted
