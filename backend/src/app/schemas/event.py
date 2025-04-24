from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Základní schéma pro Event - společné atributy
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    world_id: int # Přidáno pro vazbu při vytváření/čtení

# Schéma pro vytváření Event (vstup z API)
class EventCreate(EventBase):
    pass # world_id bude brán z URL nebo ověřeného kontextu

# Schéma pro aktualizaci Event (vstup z API)
# Všechny atributy jsou volitelné
class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

# Společné atributy uložené v DB (pro interní použití)
class EventInDBBase(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Původně orm_mode

# Finální schéma pro čtení Event (výstup z API)
class Event(EventInDBBase):
    pass 