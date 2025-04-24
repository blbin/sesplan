from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas
from app.api import dependencies # Use the correct import path
from app.db.session import get_db # Correct import for get_db
from app.auth.auth import get_current_user # Correct import for get_current_user
# Import RoleEnum explicitly
from app.models.world_user import RoleEnum, WorldUser
# Import for LocationTag schema
from app.schemas.location_tag import LocationTag

router = APIRouter()

@router.post("/", response_model=schemas.Location)
async def create_location(
    *,
    db: Session = Depends(get_db),
    location_in: schemas.LocationCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create a new location within a specific world. User must own the world."""
    # Verify ownership before creating
    await dependencies.verify_world_owner(world_id=location_in.world_id, current_user=current_user, db=db)

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
    await dependencies.verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

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
    await dependencies.verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

    location = crud.delete_location(db=db, db_location=db_location)
    return location

# --- Endpoints for managing location tags ---

@router.post(
    "/{location_id}/tags/{tag_type_id}", 
    response_model=schemas.LocationTag, # Vrátíme vytvořené přiřazení
    status_code=status.HTTP_201_CREATED,
    summary="Přiřadit tag k lokaci"
)
async def add_tag_to_location_endpoint(
    location_id: int = Path(..., description="ID lokace"),
    tag_type_id: int = Path(..., description="ID typu tagu, který se má přiřadit"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Přiřadí existující typ tagu ke konkrétní lokaci. Vyžaduje vlastnictví světa lokace."""
    # 1. Získáme lokaci
    db_location = crud.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    # 2. Ověříme vlastnictví světa
    await dependencies.verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

    # 3. CRUD operace pro přidání tagu (ta obsahuje validaci tag_type_id a world_id)
    try:
        db_association = crud.add_tag_to_location(db=db, location_id=location_id, tag_type_id=tag_type_id)
    except ValueError as e:
        # Chyby z CRUD (nenalezeno, jiný svět) převedeme na HTTP chyby
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            
    # Načteme i tag_type pro response_model
    db.refresh(db_association, attribute_names=["tag_type"])
    return db_association

@router.delete(
    "/{location_id}/tags/{tag_type_id}", 
    status_code=status.HTTP_204_NO_CONTENT, # Standardní odpověď pro úspěšné smazání
    summary="Odebrat tag z lokace"
)
async def remove_tag_from_location_endpoint(
    location_id: int = Path(..., description="ID lokace"),
    tag_type_id: int = Path(..., description="ID typu tagu, který se má odebrat"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Odebere přiřazení typu tagu od konkrétní lokace. Vyžaduje vlastnictví světa lokace."""
    # 1. Získáme lokaci (pro ověření vlastnictví světa)
    db_location = crud.get_location(db, location_id=location_id)
    if not db_location:
        # Pokud lokace neexistuje, tag stejně nemůže být přiřazen
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    # 2. Ověříme vlastnictví světa
    await dependencies.verify_world_owner(world_id=db_location.world_id, current_user=current_user, db=db)

    # 3. CRUD operace pro odebrání tagu
    deleted = crud.remove_tag_from_location(db=db, location_id=location_id, tag_type_id=tag_type_id)
    
    if not deleted:
        # Pokud nebylo nic smazáno, znamená to, že tag nebyl k lokaci přiřazen
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not associated with this location")

    # Při úspěchu nevracíme žádný obsah (status 204)
    return 