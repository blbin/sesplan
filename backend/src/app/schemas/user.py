from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserSimple(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
        from_attributes = True

# Schema for updating user information
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True