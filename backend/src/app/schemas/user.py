from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserInDB(BaseModel):
    id: int
    email: str
    username: str
    hashed_password: str