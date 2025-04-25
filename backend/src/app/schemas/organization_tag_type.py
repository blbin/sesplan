"""Schemas for OrganizationTagType model."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationTagTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    # world_id will be added during creation based on the context (e.g., path parameter)

class OrganizationTagTypeCreate(OrganizationTagTypeBase):
    world_id: int # Required during creation logic

class OrganizationTagTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class OrganizationTagTypeInDBBase(OrganizationTagTypeBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class OrganizationTagType(OrganizationTagTypeInDBBase):
    pass

# Properties stored in DB
class OrganizationTagTypeInDB(OrganizationTagTypeInDBBase):
    pass 