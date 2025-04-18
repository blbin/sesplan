from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas
from app.api import dependencies # Use the correct import path
from app.db.session import get_db # Correct import for get_db
from app.auth.auth import get_current_user # Correct import for get_current_user
# Import RoleEnum explicitly
from app.models.world_user import RoleEnum, WorldUser

router = APIRouter()

async def verify_world_owner(world_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Dependency to verify if the current user owns the world."""
    # Use a direct query to check for the OWNER association
    is_owner = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == world_id,
            WorldUser.user_id == current_user.id,
            WorldUser.role == RoleEnum.OWNER
        )
        .first()
    )
    if not is_owner:
        # Optional: Check if the world itself exists to provide a better error message
        world = crud.get_world(db, world_id=world_id)
        if not world:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions, must be world owner")
    # No need to return anything specific, the check passed if no exception was raised

@router.post("/", response_model=schemas.Location)
async def create_location(
    *,
    db: Session = Depends(get_db),
    location_in: schemas.LocationCreate,
    current_user: models.User = Depends(get_current_user) # Inject current user
    # Add dependency to verify world ownership based on location_in.world_id
    # We need to call verify_world_owner, but it needs world_id BEFORE this function body
    # Solution: Pass world_id from location_in to a dependency
):
    """Create a new location within a specific world. User must own the world."""
    # Verify ownership before creating
    await verify_world_owner(world_id=location_in.world_id, current_user=current_user, db=db)

    # Verify parent_location_id if provided
    if location_in.parent_location_id:
        parent_location = crud.get_location(db, location_id=location_in.parent_location_id)
        if not parent_location or parent_location.world_id != location_in.world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent_location_id")

    location = crud.create_location(db=db, location=location_in)
    return location

@router.get("/{location_id}", response_model=schemas.Location)
def read_location(
    *,
    db: Session = Depends(get_db),
    location_id: int,
    # current_user: models.User = Depends(get_current_user) # Maybe needed later for access control
):
    """Get a specific location by ID."""
    db_location = crud.get_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    # TODO: Add permission check? Maybe only world members can see locations?
    return db_location

@router.get("/", response_model=List[schemas.Location])
def read_locations_by_world(
    *,
    db: Session = Depends(get_db),
    world_id: int = Query(..., description="Filter locations by world ID"),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(get_current_user) # Maybe needed later for access control
):
    """Retrieve locations belonging to a specific world."""
    # TODO: Add permission check? Maybe only world members can see locations?
    locations = crud.get_locations_by_world(db, world_id=world_id, skip=skip, limit=limit)
    return locations

@router.put("/{location_id}", response_model=schemas.Location)
async def update_location(
    *,
    db: Session = Depends(get_db),
    location_id: int,
    location_in: schemas.LocationUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """Update a location. User must own the world the location belongs to."""
    db_location = crud.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    # Verify ownership of the world the location belongs to
    await verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

    # Verify new parent_location_id if provided
    if location_in.parent_location_id is not None:
        if location_in.parent_location_id == db_location.id:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location cannot be its own parent")
        parent_location = crud.get_location(db, location_id=location_in.parent_location_id)
        if not parent_location or parent_location.world_id != db_location.world_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent_location_id for this world")

    location = crud.update_location(db=db, db_location=db_location, location_in=location_in)
    return location

@router.delete("/{location_id}", response_model=schemas.Location)
async def delete_location(
    *,
    db: Session = Depends(get_db),
    location_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Delete a location. User must own the world the location belongs to."""
    db_location = crud.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    # Verify ownership of the world
    await verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

    location = crud.delete_location(db=db, db_location=db_location)
    return location 