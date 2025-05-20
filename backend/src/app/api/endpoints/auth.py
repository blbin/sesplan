from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.session import get_db
from app.schemas.token import Token
from app.core.limiter import limiter
from app.core.config import settings

# Imports for password reset
from app.schemas.password_reset import PasswordResetRequest, PasswordReset
from app.crud import crud_user, crud_password_reset_token
from app.models.user import User as UserModelDB # Renamed to avoid conflict with schema
from app.core.email import send_password_reset_email
from app.core.security import get_password_hash # For hashing new password
import secrets
from datetime import datetime, timezone # Ensure timezone is imported

router = APIRouter()

@router.post("/token", response_model=Token)
@limiter.limit(settings.AUTH_LOGIN_LIMIT)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user: UserModelDB | None = crud_user.get_user_by_email(db, email=reset_request.email)

    if user:
        # Delete any existing tokens for this user
        crud_password_reset_token.delete_all_password_reset_tokens_for_user(db, user_id=user.id)

        # Generate a new token
        generated_token = secrets.token_urlsafe(32)
        # Tokens valid for 1 hour
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1) # Use timezone.utc

        # Store the token
        crud_password_reset_token.create_password_reset_token(
            db,
            user_id=user.id,
            token=generated_token,
            expires_at=expires_at
        )

        # Construct reset link (use settings.DOMAIN or placeholder)
        # reset_link = f"https://{settings.DOMAIN}/reset-password?token={generated_token}"
        reset_link = f"https://yourfrontend.com/reset-password?token={generated_token}" # Placeholder

        send_password_reset_email(email_to=user.email, reset_link=reset_link)

    # Generic response to prevent email enumeration
    return {"msg": "If an account with this email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    valid_token = crud_password_reset_token.get_password_reset_token_by_token(db, token=reset_data.token)

    if not valid_token or valid_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )

    user = crud_user.get_user(db, user_id=valid_token.user_id)
    if not user:
        # This should ideally not happen if DB integrity is maintained
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    hashed_password = get_password_hash(reset_data.new_password)
    crud_user.update_password(db, user=user, new_password_hash=hashed_password)

    # Delete the token now that it's been used
    crud_password_reset_token.delete_password_reset_token(db, token_id=valid_token.id)

    return {"msg": "Password has been reset successfully."}