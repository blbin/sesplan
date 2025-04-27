from sqlalchemy.orm import Session
from typing import Optional

# Importuj modely relativně k aktuálnímu adresáři (crud)
from ..models.world_user import WorldUser 
# RoleEnum může být potřeba, pokud bychom přidávali další funkce sem
# from ..models.world_user import RoleEnum 

# Helper function to get user membership and role in a world
def get_world_membership_with_role(db: Session, world_id: int, user_id: int) -> Optional[WorldUser]:
    """Fetches the WorldUser association including the role."""
    return db.query(WorldUser).filter(
        WorldUser.world_id == world_id,
        WorldUser.user_id == user_id
    ).first()

# Zde mohou být v budoucnu další CRUD funkce pro WorldUser
# např. add_world_member, remove_world_member, update_world_member_role 