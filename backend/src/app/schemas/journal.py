from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Forward declaration for JournalEntry
# from .journal_entry import JournalEntry # Avoid circular import for now

# Base properties shared by all schemas
class JournalBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties required for creation - REMOVED (JournalCreate)
# Journal is created automatically with Character

# Properties required for update (all optional)
class JournalUpdate(JournalBase):
    name: Optional[str] = None # Override base to make it optional
    description: Optional[str] = None 
    # character_id cannot be updated

# Properties stored in DB but not returned to client directly
class JournalInDBBase(JournalBase):
    id: int
    character_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Changed from from_attributes=True for compatibility

# Properties returned to client (includes relationships)
class Journal(JournalInDBBase):
    # entries: List['JournalEntry'] = [] # Defer loading entries for performance
    pass # Keep it simple for now, can add related entries later if needed

# Properties stored in DB (needed for relationship loading in Character schema)
class JournalInDB(JournalInDBBase):
    pass 