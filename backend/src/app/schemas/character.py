from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .journal import Journal
from .character_tag import CharacterTag

# Base properties
class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schema for character creation
class CharacterCreate(CharacterBase):
    world_id: int # Need to specify world when creating character
    tag_type_ids: Optional[List[int]] = None # Added tag type IDs

# Schema for character update
class CharacterUpdate(CharacterBase):
    name: Optional[str] = None
    description: Optional[str] = None
    tag_type_ids: Optional[List[int]] = None # Added tag type IDs
    user_id: Optional[int | None] = Field(default=None) # Allow setting user_id to None explicitly if needed
    # world_id: Optional[int] = None # Maybe allow moving characters? Not now.

# Schema for assigning user to a character
class CharacterAssignUser(BaseModel):
    user_id: int | None # Allow assigning or unassigning

# Schema for reading character data
class Character(CharacterBase):
    id: int
    world_id: int
    user_id: Optional[int] = None # User assigned to the character (can be null)
    created_at: datetime
    updated_at: datetime
    journal: Optional[Journal] = None
    tags: List[CharacterTag] = []

    class Config:
        from_attributes = True 