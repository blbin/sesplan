"""Schemas for Location model."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    pass


# Properties properties stored in DB
class LocationInDB(LocationInDBBase):
    pass 