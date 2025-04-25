from pydantic import BaseModel
from datetime import datetime

# Základní schéma pro data, která se vrací
class ItemTagTypeBase(BaseModel):
    name: str

# Schéma pro vytváření
class ItemTagTypeCreate(ItemTagTypeBase):
    pass

# Schéma pro aktualizaci
class ItemTagTypeUpdate(ItemTagTypeBase):
    name: str | None = None # Volitelné při aktualizaci

# Schéma pro data uložená v DB (pro čtení)
class ItemTagTypeInDBBase(ItemTagTypeBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic v2 style

# Finální schéma pro čtení dat z API
class ItemTagType(ItemTagTypeInDBBase):
    pass 