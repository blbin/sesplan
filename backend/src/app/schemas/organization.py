"""Schemas for Organization model."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import the tag schema to embed it
from .organization_tag import OrganizationTag 

# Schemas for related models might be needed later (e.g., for Character, Tags)

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_organization_id: Optional[int] = None


class OrganizationCreate(OrganizationBase):
    world_id: int


class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255) # All fields optional for update
    # world_id is not updatable
    # parent_organization_id can be set to null or other organization

class OrganizationInDBBase(OrganizationBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Replaces orm_mode = True


# Properties to return to client
class Organization(OrganizationInDBBase):
    tags: List[OrganizationTag] = [] # Include assigned tags
    # Add relationships to be returned if needed, e.g.:
    # child_organizations: List['Organization'] = [] # Requires forward ref handling or separate schema
    # pass # Keep it simple for now - REMOVED


# Properties stored in DB
class OrganizationInDB(OrganizationInDBBase):
    pass

# Self-referencing for potential nested structures if needed later
# Organization.model_rebuild() 