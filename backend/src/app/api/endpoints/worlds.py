from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional, Set

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

# Endpoint to get all characters within a specific world (with pagination)
@router.get("/{world_id}/characters/", response_model=List[schemas.Character])
def read_world_characters(
    world_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(get_current_user) # Re-add if needed
):
    """Retrieve all characters belonging to a specific world with pagination."""
    # TODO: Verify user has access to this world if necessary (e.g., public world or member)
    db_world = crud.get_world(db, world_id=world_id)
    if db_world is None:
        raise HTTPException(status_code=404, detail="World not found")
    
    # Use the correct paginated CRUD function: get_characters_by_world
    characters = crud.get_characters_by_world(db, world_id=world_id, skip=skip, limit=limit)
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

@router.get("/{world_id}/campaign_users", response_model=List[schemas.UserSimple])
@limiter.limit(settings.GENERIC_READ_LIMIT)
async def get_campaign_users_in_world(
    *,
    request: Request, # Added for limiter
    world_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a unique list of users participating in any campaign within a specific world.
    Requires the current user to be a member of the world.
    """
    # 1. Check if world exists
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")

    # 2. Check if current user is a member of the world
    membership = await get_world_membership(world_id, current_user.id, db)
    # Allow public access if world is public?
    # if not membership and not db_world.is_public: 
    if not membership:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this world")

    # 3. Get all campaigns in the world
    campaigns = crud.get_campaigns_by_world(db, world_id=world_id)
    if not campaigns:
        return [] # No campaigns in this world, so no campaign users

    campaign_ids = [campaign.id for campaign in campaigns]

    # 4. Get all unique user IDs from CampaignUser for these campaigns
    campaign_user_ids: Set[int] = set()
    campaign_users_assoc = (
        db.query(models.UserCampaign.user_id)
        .filter(models.UserCampaign.campaign_id.in_(campaign_ids))
        .distinct()
        .all()
    )
    campaign_user_ids = {user_id_tuple[0] for user_id_tuple in campaign_users_assoc}
    
    if not campaign_user_ids:
        return [] # No users found in any campaign

    # 5. Get user details for these IDs
    users = crud.get_users_by_ids(db, user_ids=list(campaign_user_ids))

    return users 