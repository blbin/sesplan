from pydantic import BaseModel
from datetime import datetime
from .character_tag_type import CharacterTagType # Import pro vnoření

# Schéma pro data čtená z databáze (základní)
class CharacterTagBase(BaseModel):
    character_id: int
    character_tag_type_id: int

# Schéma pro vytváření tagu (stačí ID typu tagu, character_id se vezme z cesty)
class CharacterTagCreate(BaseModel):
    character_tag_type_id: int

# Schéma pro data uložená v DB
class CharacterTagInDBBase(CharacterTagBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Finální schéma pro čtení z API (může obsahovat vnořený typ tagu)
class CharacterTag(CharacterTagInDBBase):
    tag_type: CharacterTagType | None = None # Vnořený objekt typu tagu 