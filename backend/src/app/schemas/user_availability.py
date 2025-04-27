from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

# Import UserSimple for embedding user info
from .user import UserSimple 

# Base schema with common attributes
class UserAvailabilityBase(BaseModel):
    available_from: datetime
    available_to: datetime
    note: Optional[str] = None

    @field_validator('available_to')
    def check_dates(cls, v, values):
        # Pydantic v2: 'values' might be passed differently, adjust if needed
        # This depends on exact Pydantic version and how validation context is handled
        # For simplicity, let's assume 'available_from' is already validated and present
        # A more robust approach might involve model-level validation
        if 'available_from' in values.data and v <= values.data['available_from']:
            raise ValueError('available_to must be after available_from')
        return v

# Schema for creating/updating user availability (input)
# user_id will come from the current authenticated user
# slot_id will come from the path parameter
class UserAvailabilityCreateUpdate(UserAvailabilityBase):
    pass

# Schema for reading user availability (output)
class UserAvailability(UserAvailabilityBase):
    id: int
    user_id: int
    slot_id: int
    user: UserSimple # Embed simplified user information
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 