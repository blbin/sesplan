from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Základní schéma pro LocationTagType
class LocationTagTypeBase(BaseModel):
    name: str
    # Přidáme další atributy jako barva, popis později, pokud budou potřeba

# Schéma pro vytváření LocationTagType (vstup)
class LocationTagTypeCreate(LocationTagTypeBase):
    pass

# Schéma pro aktualizaci LocationTagType (vstup)
class LocationTagTypeUpdate(BaseModel):
    name: Optional[str] = None

# Společné atributy uložené v DB
class LocationTagTypeInDBBase(LocationTagTypeBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Finální schéma pro čtení LocationTagType (výstup)
class LocationTagType(LocationTagTypeInDBBase):
    pass 