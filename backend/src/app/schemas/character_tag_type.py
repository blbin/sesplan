from pydantic import BaseModel
from datetime import datetime

# Základní schéma pro data, která se vrací
class CharacterTagTypeBase(BaseModel):
    name: str

# Schéma pro vytváření
class CharacterTagTypeCreate(CharacterTagTypeBase):
    pass

# Schéma pro aktualizaci
class CharacterTagTypeUpdate(CharacterTagTypeBase):
    name: str | None = None # Všechny fieldy jsou volitelné při aktualizaci

# Schéma pro data uložená v DB (pro čtení)
class CharacterTagTypeInDBBase(CharacterTagTypeBase):
    id: int
    world_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # Umožní mapování z SQLAlchemy modelu

# Finální schéma pro čtení dat z API
class CharacterTagType(CharacterTagTypeInDBBase):
    pass 