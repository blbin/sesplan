from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.user_campaign import CampaignRoleEnum # Import enum
from .user import User # Import User schema for nesting

# Base schema - not directly used often but good practice
class UserCampaignBase(BaseModel):
    user_id: int
    campaign_id: int
    role: CampaignRoleEnum

# Schema for updating a member's role
class UserCampaignUpdate(BaseModel):
    role: CampaignRoleEnum

# Schema for reading association data (potentially nested)
class UserCampaignRead(UserCampaignBase):
    id: int
    user: User # Include user details
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 