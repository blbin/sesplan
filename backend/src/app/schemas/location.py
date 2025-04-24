"""Schemas for Location model."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Importujeme schéma LocationTag
from .location_tag import LocationTag


class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_location_id: Optional[int] = None


class LocationCreate(LocationBase):
    world_id: int


class LocationUpdate(LocationBase):
    name: Optional[str] = None # All fields optional for update
    # world_id is not updatable here, maybe move world required? No. 
    # parent_location_id can be set to null or other location


# Properties shared by models stored in DB
class LocationInDBBase(LocationBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Replaces orm_mode = True


# Properties to return to client
class Location(LocationInDBBase):
    tags: List[LocationTag] = [] # Přidáme pole pro tagy


# Properties properties stored in DB
class LocationInDB(LocationInDBBase):
    pass 