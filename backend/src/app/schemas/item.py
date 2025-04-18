"""Schemas for Item model."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Základní schéma s poli sdílenými mezi vytvářením a čtením
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the item")
    description: Optional[str] = None
    # character_id a location_id jsou volitelné a nastavují se při vytváření/aktualizaci
    character_id: Optional[int] = None
    location_id: Optional[int] = None

# Schéma pro vytváření nového itemu (vyžaduje world_id)
class ItemCreate(ItemBase):
    world_id: int

# Schéma pro aktualizaci itemu (všechna pole jsou volitelná)
# world_id se nemění
class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Name of the item")
    description: Optional[str] = None
    character_id: Optional[int] = None # Může být None pro odstranění přiřazení
    location_id: Optional[int] = None # Může být None pro odstranění přiřazení

# Schéma pro čtení itemu z databáze (zahrnuje ID a časová razítka)
class ItemInDBBase(ItemBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schéma pro vracení itemu klientovi (může se v budoucnu lišit od DB schématu)
class Item(ItemInDBBase):
    pass

# Schéma pro reprezentaci itemu v databázi
class ItemInDB(ItemInDBBase):
    pass 