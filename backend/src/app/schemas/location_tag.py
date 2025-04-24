from pydantic import BaseModel
from datetime import datetime
from typing import Optional # Potřebujeme Optional

# Importujeme schéma pro LocationTagType, abychom ho mohli vnořit
from .location_tag_type import LocationTagType 

# Základní schéma pro LocationTag - obsahuje ID spojení a ID typu tagu
class LocationTagBase(BaseModel):
    location_tag_type_id: int
    # location_id nepotřebujeme explicitně, bude v kontextu Location

# Schéma pro čtení LocationTag (výstup)
# Obsahuje detaily o samotném spojení a vnořený typ tagu
class LocationTag(BaseModel):
    id: int # ID samotného záznamu v location_tags
    location_id: int
    location_tag_type_id: int
    created_at: datetime
    tag_type: Optional[LocationTagType] = None # Vnořené schéma pro typ tagu

    class Config:
        from_attributes = True 