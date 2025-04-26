from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ...models.world_user import RoleEnum as WorldRoleEnum # Import role enum
from ...core.limiter import limiter # Import limiteru
from ...core.config import settings # Import settings

router = APIRouter(tags=["worlds"])

# Helper function to check world membership/role
async def get_world_membership(world_id: int, user_id: int, db: Session = Depends(get_db)) -> models.WorldUser | None:
    return db.query(models.WorldUser).filter(
        models.WorldUser.world_id == world_id,
        models.WorldUser.user_id == user_id
    ).first()

@router.post("/", response_model=schemas.World, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
def create_world(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    world_in: schemas.WorldCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create new world. Creator becomes OWNER."""
    world = crud.create_world(db=db, world=world_in, creator_id=current_user.id)
    return world

@router.get("/public", response_model=List[schemas.World])
@limiter.limit(settings.GENERIC_READ_LIMIT) # Přidán read limit
def read_public_worlds(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve worlds where the current user is the OWNER."""
    # Použijeme upravenou CRUD funkci
    worlds = crud.get_worlds_by_owner(db, user_id=current_user.id, skip=skip, limit=limit)
    return worlds

@router.get("/", response_model=List[schemas.World])
@limiter.limit(settings.GENERIC_READ_LIMIT) # Přidán read limit
def read_worlds(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve worlds where the current user is the OWNER."""
    # Použijeme upravenou CRUD funkci
    worlds = crud.get_worlds_by_owner(db, user_id=current_user.id, skip=skip, limit=limit)
    return worlds

@router.get("/{world_id}", response_model=schemas.World)
@limiter.limit(settings.GENERIC_READ_LIMIT) # Přidán read limit
async def read_world(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    world_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Get world by ID. Requires membership in the world."""
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    # Check if the current user is a member of the world
    membership = await get_world_membership(world_id, current_user.id, db)
    if not membership and not world.is_public: # Allow access if public
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to access this world")

    return world

@router.put("/{world_id}", response_model=schemas.World)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
async def update_world(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    world_id: int,
    world_in: schemas.WorldUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """Update a world. Requires OWNER role."""
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    # Check if the current user is the OWNER
    membership = await get_world_membership(world_id, current_user.id, db)
    if not membership or membership.role != WorldRoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (Owner required)")

    world = crud.update_world(db=db, db_world=db_world, world_in=world_in)
    return world

@router.delete("/{world_id}", response_model=schemas.World)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
async def delete_world(
    *,
    request: Request, # Přidáno pro limiter
    db: Session = Depends(get_db),
    world_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Delete a world. Requires OWNER role."""
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    # Check if the current user is the OWNER
    membership = await get_world_membership(world_id, current_user.id, db)
    if not membership or membership.role != WorldRoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (Owner required)")

    # CRUD funkce provede smazání
    deleted_world = crud.delete_world(db=db, db_world=db_world)
    return deleted_world

# Endpoint pro získání kampaní v rámci světa
@router.get("/{world_id}/campaigns/", response_model=List[schemas.Campaign])
def read_world_campaigns(
    *,
    db: Session = Depends(get_db),
    world_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve campaigns within a specific world owned by the current user.
    """
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    if world.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    campaigns = crud.get_campaigns_by_world(db, world_id=world_id, skip=skip, limit=limit)
    return campaigns

# Nový endpoint pro získání postav v rámci světa
@router.get("/{world_id}/characters/", response_model=List[schemas.Character])
async def read_world_characters(
    *,
    db: Session = Depends(get_db),
    world_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve all characters within a specific world. Requires world membership."""
    # Ověření členství ve světě
    membership = await get_world_membership(world_id, current_user.id, db)
    if not membership:
        # Zde bychom mohli zkontrolovat i public status světa, pokud chceme
        # public světy zpřístupnit i nečlenům, ale pro postavy to nemusí dávat smysl.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this world")

    characters = crud.get_all_characters_in_world(db, world_id=world_id, skip=skip, limit=limit)
    return characters

@router.get("/{world_id}/members", response_model=List[schemas.WorldUserRead])
@limiter.limit(settings.GENERIC_READ_LIMIT) # Přidán read limit
async def read_world_members(
    *,
    request: Request, # Přidáno pro limiter
    world_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve members of a world."""
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    if world.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    members = crud.get_world_members(db, world_id=world_id, skip=skip, limit=limit)
    return members

@router.post("/{world_id}/members", response_model=schemas.WorldUserRead)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
async def add_world_member(
    *,
    request: Request, # Přidáno pro limiter
    world_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a member to a world."""
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    if world.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    member = crud.add_world_member(db, world_id=world_id, user_id=user_id)
    return member

@router.put("/{world_id}/members/{user_id}", response_model=schemas.WorldUserRead)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
async def update_world_member_role(
    *,
    request: Request, # Přidáno pro limiter
    world_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update the role of a member in a world."""
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    if world.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    member = crud.update_world_member_role(db, world_id=world_id, user_id=user_id)
    return member

@router.delete("/{world_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.GENERIC_WRITE_LIMIT) # Přidán write limit
async def remove_world_member(
    *,
    request: Request, # Přidáno pro limiter
    world_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a member from a world."""
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    if world.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    crud.remove_world_member(db, world_id=world_id, user_id=user_id) 