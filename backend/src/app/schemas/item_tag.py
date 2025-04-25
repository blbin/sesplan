from pydantic import BaseModel
from datetime import datetime
from .item_tag_type import ItemTagType # Import pro vnoření

# Schéma pro data čtená z databáze (základní)
class ItemTagBase(BaseModel):
    item_id: int
    item_tag_type_id: int

# Schéma pro vytváření tagu (stačí ID typu tagu, item_id se vezme z cesty)
class ItemTagCreate(BaseModel):
    item_tag_type_id: int

# Schéma pro data uložená v DB
class ItemTagInDBBase(ItemTagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Finální schéma pro čtení z API (může obsahovat vnořený typ tagu)
class ItemTag(ItemTagInDBBase):
    tag_type: ItemTagType | None = None # Vnořený objekt typu tagu 