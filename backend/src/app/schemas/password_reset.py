from pydantic import BaseModel, EmailStr

class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.
    Requires the user's email address.
    """
    email: EmailStr

class PasswordReset(BaseModel):
    """
    Schema for resetting a password using a token.
    Requires the reset token and the new password.
    """
    token: str
    new_password: str
