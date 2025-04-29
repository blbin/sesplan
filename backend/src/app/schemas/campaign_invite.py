from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base properties (not directly used for create/update but good practice)
class CampaignInviteBase(BaseModel):
    campaign_id: int
    token: str
    max_uses: Optional[int] = None
    uses: int = 0
    expires_at: Optional[datetime] = None

# Schema for creating an invite (input)
# Token is generated server-side
class CampaignInviteCreate(BaseModel):
    max_uses: Optional[int] = 1 # Default to single use
    expires_at: Optional[datetime] = None

# Schema for reading invite data (output)
class CampaignInvite(CampaignInviteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Maybe add campaign details if needed?

    class Config:
        from_attributes = True

# Schema for the response when accepting an invite
class CampaignInviteAcceptResponse(BaseModel):
    message: str
    campaign_id: int
    role: str
    character_id: Optional[int] = None 