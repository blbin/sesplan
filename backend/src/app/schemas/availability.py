from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import User # Import User schema

# Base schema with common attributes
class AvailabilityBase(BaseModel):
    available_from: datetime
    available_to: datetime
    note: Optional[str] = None

# Schema for creating an availability record (input)
# user_id will come from the current authenticated user
# session_id will come from the path parameter
class AvailabilityCreate(AvailabilityBase):
    pass

# Schema for updating an availability record (input)
class AvailabilityUpdate(AvailabilityBase):
    pass

# Schema for reading an availability record (output)
class Availability(AvailabilityBase):
    id: int
    user_id: int
    session_id: int
    user: User # Add the user field
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # Enable ORM mode for SQLAlchemy model conversion 