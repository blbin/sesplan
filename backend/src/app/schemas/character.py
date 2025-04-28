from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .character_tag import CharacterTag

# Base properties shared by all schemas
class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: Optional[int] = None # Character might not be linked to a user (NPC)
    world_id: int # Character must belong to a world

# Properties required for creation
class CharacterCreate(CharacterBase):
    name: str # Ensure name is required on creation
    world_id: int # Ensure world is specified

# Properties required for update (all optional)
class CharacterUpdate(CharacterBase):
    name: Optional[str] = None # Override base to make it optional for update
    world_id: Optional[int] = None # World shouldn't typically change, but allow if needed

# Properties stored in DB but not returned to client directly
class CharacterInDBBase(CharacterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # Use orm_mode for older Pydantic or from_attributes=True for v2

# Properties returned to client (can include relationships later if needed)
class Character(CharacterInDBBase):
    tags: List[CharacterTag] = []

# Simplified schema for lists or nested objects
class CharacterSimple(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Properties stored in DB (internal use)
class CharacterInDB(CharacterInDBBase):
    pass

# Schema for assigning user to a character (missing)
class CharacterAssignUser(BaseModel):
    user_id: Optional[int] = None # Allow assigning (int) or unassigning (None)