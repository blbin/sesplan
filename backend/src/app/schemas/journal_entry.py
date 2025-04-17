from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties shared by all schemas
class JournalEntryBase(BaseModel):
    title: Optional[str] = None
    content: str

# Properties required for creation
class JournalEntryCreate(JournalEntryBase):
    journal_id: int

# Properties required for update (all optional)
class JournalEntryUpdate(JournalEntryBase):
    title: Optional[str] = None # Already optional in base
    content: Optional[str] = None # Override base to make it optional
    # journal_id cannot be updated

# Properties stored in DB but not returned to client directly
class JournalEntryInDBBase(JournalEntryBase):
    id: int
    journal_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Changed from from_attributes=True for compatibility

# Properties returned to client
class JournalEntry(JournalEntryInDBBase):
    pass

# Properties stored in DB (needed for relationship loading in Journal schema)
class JournalEntryInDB(JournalEntryInDBBase):
    pass 