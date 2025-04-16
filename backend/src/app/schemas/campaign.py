from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Základní vlastnosti
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None

# Schéma pro vytváření kampaně
class CampaignCreate(CampaignBase):
    world_id: int # Při vytváření kampaně musíme specifikovat svět

# Schéma pro úpravu kampaně
class CampaignUpdate(CampaignBase):
    name: Optional[str] = None
    world_id: Optional[int] = None # Možná chceme umožnit přesun kampaně? Zatím ne.

# Schéma pro čtení dat kampaně
class Campaign(CampaignBase):
    id: int
    world_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # orm_mode = True
        from_attributes = True 