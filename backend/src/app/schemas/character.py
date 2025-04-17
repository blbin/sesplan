from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties
class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schema for character creation
class CharacterCreate(CharacterBase):
    world_id: int # Need to specify world when creating character

# Schema for character update
class CharacterUpdate(CharacterBase):
    name: Optional[str] = None
    description: Optional[str] = None
    # world_id: Optional[int] = None # Maybe allow moving characters? Not now.

# Schema for reading character data
class Character(CharacterBase):
    id: int
    world_id: int
    user_id: int # User who created the character
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 