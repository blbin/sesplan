from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .campaign import Campaign  # Import pro vnořené schéma

# Základní vlastnosti sdílené mezi schématy
class WorldBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False # Přidáno is_public místo is_private

# Schéma pro vytváření světa (přijímaná data z API)
class WorldCreate(WorldBase):
    pass

# Schéma pro úpravu světa
class WorldUpdate(WorldBase):
    name: Optional[str] = None # Umožníme částečný update
    is_public: Optional[bool] = None

# Schéma pro čtení dat světa (vrácená data z API)
class World(WorldBase):
    id: int
    created_at: datetime
    updated_at: datetime
    campaigns: List[Campaign] = [] # Vracíme i seznam kampaní patřících ke světu

    class Config:
        # orm_mode = True # Povolí mapování z SQLAlchemy modelu
        from_attributes = True 