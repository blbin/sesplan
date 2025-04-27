from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# Forward declaration for UserAvailability within SessionSlot
from .user_availability import UserAvailability

# Base schema with common attributes
class SessionSlotBase(BaseModel):
    slot_from: datetime
    slot_to: datetime
    note: Optional[str] = None

# Schema for creating a session slot (input)
# session_id will come from the path parameter
class SessionSlotCreate(SessionSlotBase):
    pass

# Schema for updating a session slot (input)
class SessionSlotUpdate(SessionSlotBase):
    # All fields are optional for update
    slot_from: Optional[datetime] = None
    slot_to: Optional[datetime] = None
    note: Optional[str] = None

# Schema for reading a session slot (output)
class SessionSlot(SessionSlotBase):
    id: int
    session_id: int
    created_at: datetime
    updated_at: datetime
    # Include user availabilities when reading a slot
    user_availabilities: List[UserAvailability] = []

    model_config = ConfigDict(from_attributes=True) # Replace orm_mode 