from pydantic import BaseModel
from app.models.world_user import RoleEnum  # Import enum pro roli
from .user import User  # Import schématu uživatele pro vnoření

class WorldUserBase(BaseModel):
    user_id: int
    world_id: int
    role: RoleEnum

class WorldUserCreate(WorldUserBase):
    # Obvykle se role nastavuje při vytvoření, ale můžeme ji zde vyžadovat
    pass

class WorldUserUpdate(BaseModel):
    role: RoleEnum

# Schéma pro čtení dat z DB, včetně detailů uživatele
class WorldUserRead(WorldUserBase):
    user: User  # Vnořené schéma uživatele

    class Config:
        from_attributes = True # Povolí načítání z ORM modelu 