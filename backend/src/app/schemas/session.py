from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties shared by all schemas
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None
    date_time: Optional[datetime] = None # Allow session date/time to be optional

# Properties required for creation
class SessionCreate(SessionBase):
    campaign_id: int
    title: str # Ensure title is required on creation

# Properties required for update (all optional)
class SessionUpdate(SessionBase):
    title: Optional[str] = None # Override base to make it optional for update
    # campaign_id cannot be updated

# Properties stored in DB but not returned to client directly
class SessionInDBBase(SessionBase):
    id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime # Should always have a value due to model defaults

    class Config:
        orm_mode = True # Use orm_mode for older Pydantic or from_attributes=True for v2

# Properties returned to client (can include relationships later if needed)
class Session(SessionInDBBase):
    pass

# Properties stored in DB (internal use)
class SessionInDB(SessionInDBBase):
    pass 