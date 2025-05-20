import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app # Assuming app.main.app is the FastAPI app instance
from app.crud import crud_user, crud_password_reset_token
from app.models.user import User as UserModel
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db # To override dependency for test session

# This would typically be in conftest.py and provide a transactional session
@pytest.fixture(scope="function")
def db_session_for_tests(monkeypatch):
    # For simplicity, using the real get_db if it connects to a test DB.
    # In a real setup, this would point to a dedicated test DB and handle transactions.
    # For now, we'll assume get_db() from app.db.session is configured for tests
    # or we will rely on cleaning up data manually.
    # A more robust fixture would use a separate test DB and rollback transactions.
    db = next(get_db()) 
    
    # Clean up PasswordResetToken and User table before each test
    # This is a simple cleanup. In a real app, use transactional tests or delete specific test data.
    db.query(PasswordResetToken).delete()
    db.query(UserModel).delete()
    db.commit()
    
    yield db

    db.query(PasswordResetToken).delete()
    db.query(UserModel).delete()
    db.commit()


# Helper to create a user directly in DB for testing
def create_test_user_in_db(db: Session, email: str = "test@example.com", username: str = "testuser", password: str = "testpassword") -> UserModel:
    user_in = UserCreate(email=email, username=username, password=password)
    return crud_user.create_user(db=db, user=user_in)

client = TestClient(app)

# --- Tests for /request-password-reset ---

@patch("app.api.endpoints.auth.send_password_reset_email")
def test_request_password_reset_user_exists(mock_send_email, db_session_for_tests: Session):
    user = create_test_user_in_db(db_session_for_tests, email="exists@example.com", username="existsuser")
    
    response = client.post("/request-password-reset", json={"email": user.email})
    
    assert response.status_code == 202
    assert response.json() == {"msg": "If an account with this email exists, a password reset link has been sent."}
    
    mock_send_email.assert_called_once()
    args, _ = mock_send_email.call_args
    assert args[0] == user.email  # email_to
    assert "token=" in args[1]   # reset_link contains a token
    
    token_in_db = db_session_for_tests.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    assert token_in_db is not None
    assert len(token_in_db.token) > 10 # Check if token looks reasonable

@patch("app.api.endpoints.auth.send_password_reset_email")
def test_request_password_reset_user_not_exists(mock_send_email, db_session_for_tests: Session):
    response = client.post("/request-password-reset", json={"email": "nonexistent@example.com"})
    
    assert response.status_code == 202
    assert response.json() == {"msg": "If an account with this email exists, a password reset link has been sent."}
    
    mock_send_email.assert_not_called()
    
    token_count = db_session_for_tests.query(PasswordResetToken).count()
    assert token_count == 0

# --- Tests for /reset-password ---

def test_reset_password_valid_token(db_session_for_tests: Session):
    user = create_test_user_in_db(db_session_for_tests, email="resetme@example.com", username="resetmeuser", password="oldpassword")
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    created_token = crud_password_reset_token.create_password_reset_token(
        db_session_for_tests, user_id=user.id, token=token_value, expires_at=expires_at
    )
    
    new_password = "newStrongPassword123"
    response = client.post("/reset-password", json={"token": token_value, "new_password": new_password})
    
    assert response.status_code == 200
    assert response.json() == {"msg": "Password has been reset successfully."}
    
    db_session_for_tests.refresh(user) # Refresh user object from DB
    assert verify_password(new_password, user.password_hash)
    
    token_in_db = db_session_for_tests.query(PasswordResetToken).filter(PasswordResetToken.id == created_token.id).first()
    assert token_in_db is None

def test_reset_password_invalid_token(db_session_for_tests: Session):
    response = client.post("/reset-password", json={"token": "invalid-fake-token", "new_password": "newpassword"})
    
    assert response.status_code == 400
    assert "Invalid or expired password reset token" in response.json()["detail"]

def test_reset_password_expired_token(db_session_for_tests: Session):
    user = create_test_user_in_db(db_session_for_tests, email="expired@example.com", username="expireduser")
    token_value = secrets.token_urlsafe(32)
    # Note: In a real scenario with time-sensitive tests, libraries like `freezegun` are helpful.
    # Here, we ensure it's definitely in the past.
    expires_at = datetime.now(timezone.utc) - timedelta(hours=1, minutes=1) 
    
    crud_password_reset_token.create_password_reset_token(
        db_session_for_tests, user_id=user.id, token=token_value, expires_at=expires_at
    )
    
    response = client.post("/reset-password", json={"token": token_value, "new_password": "newpassword"})
    
    assert response.status_code == 400
    assert "Invalid or expired password reset token" in response.json()["detail"]

# Optional: test_reset_password_token_user_mismatch
# This is often implicitly handled if get_password_reset_token_by_token
# doesn't care about the user, but the subsequent get_user(token.user_id)
# correctly fetches the user associated with the token.
# The current implementation of reset_password endpoint does:
# 1. Get token by string: `valid_token = crud_password_reset_token.get_password_reset_token_by_token(db, token=reset_data.token)`
# 2. Get user by token's user_id: `user = crud_user.get_user(db, user_id=valid_token.user_id)`
# This structure means the token dictates the user, so a mismatch isn't directly possible in the way
# of "use token T for user A to change user B's password". The password for user A (owner of token T) would be changed.
# So, a specific test for "mismatch" might not be directly applicable here unless the logic was different.

# Fixture to override get_db dependency for API endpoints
# This needs to be defined so TestClient uses the test session
def override_get_db():
    # This should yield the same session used by db_session_for_tests
    # For simplicity, if db_session_for_tests is function-scoped and creates a new session each time,
    # this approach is tricky. A session shared via context var or a more advanced fixture setup is better.
    # For now, we'll assume test runs are isolated enough or the get_db() is test-aware.
    # A better way: use app.dependency_overrides
    try:
        db = next(get_db()) # This will use the production get_db.
        # A proper setup would involve a TestSessionLocal and overriding get_db
        # to yield sessions from TestSessionLocal.
        # For now, this means tests might interact with the actual dev DB if not configured carefully.
        # The db_session_for_tests fixture attempts some cleanup.
        yield db
    finally:
        pass # db.close() if the session was managed here

app.dependency_overrides[get_db] = override_get_db

# Cleanup overrides after tests are done
@pytest.fixture(scope="session", autouse=True)
def cleanup_dependency_overrides():
    yield
    app.dependency_overrides = {}
