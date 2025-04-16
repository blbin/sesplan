from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user

router = APIRouter(tags=["worlds"])

@router.post("/", response_model=schemas.World)
def create_world(
    *,
    db: Session = Depends(get_db),
    world_in: schemas.WorldCreate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Create new world.
    """
    world = crud.create_world(db=db, world=world_in, owner_id=current_user.id)
    return world

@router.get("/", response_model=List[schemas.World])
def read_worlds(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve worlds owned by the current user.
    """
    worlds = crud.get_worlds_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return worlds

@router.get("/{world_id}", response_model=schemas.World)
def read_world(
    *,
    db: Session = Depends(get_db),
    world_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get world by ID.
    """
    world = crud.get_world(db, world_id=world_id)
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    if world.owner_id != current_user.id:
         # Můžeme přidat logiku pro adminy nebo sdílené světy později
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return world

@router.put("/{world_id}", response_model=schemas.World)
def update_world(
    *,
    db: Session = Depends(get_db),
    world_id: int,
    world_in: schemas.WorldUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a world.
    """
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=404, detail="World not found")
    if db_world.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    world = crud.update_world(db=db, db_world=db_world, world_in=world_in)
    return world

@router.delete("/{world_id}", response_model=schemas.World)
def delete_world(
    *,
    db: Session = Depends(get_db),
    world_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a world.
    """
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=404, detail="World not found")
    if db_world.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    world = crud.delete_world(db=db, db_world=db_world)
    return world

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