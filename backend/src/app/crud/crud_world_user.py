from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.exc import IntegrityError

# Importuj modely relativně k aktuálnímu adresáři (crud)
from ..models.world_user import WorldUser 
# RoleEnum může být potřeba, pokud bychom přidávali další funkce sem
from ..models.world_user import RoleEnum 
# Potřebujeme User a World pro kontroly
from ..models import User, World

# Zde mohou být v budoucnu další CRUD funkce pro WorldUser
# např. add_world_member, remove_world_member, update_world_member_role 