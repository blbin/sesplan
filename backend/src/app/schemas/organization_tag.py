"""Schemas for OrganizationTag (association) model."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Import the schema for the related type to embed it
from .organization_tag_type import OrganizationTagType

class OrganizationTagBase(BaseModel):
    organization_id: int
    organization_tag_type_id: int

class OrganizationTagCreate(OrganizationTagBase):
    # No extra fields needed for creation, IDs are sufficient
    pass

class OrganizationTagUpdate(BaseModel):
    # Association tables are typically not updated, they are created/deleted
    pass 

class OrganizationTagInDBBase(OrganizationTagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client (embedding the tag type)
class OrganizationTag(OrganizationTagInDBBase):
    tag_type: Optional[OrganizationTagType] = None # Embed the tag type details

# Properties stored in DB
class OrganizationTagInDB(OrganizationTagInDBBase):
    pass 