from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import List, Set
from ..models.location import Location
from ..models.location_tag import LocationTag
from ..schemas.location import LocationCreate, LocationUpdate


def get_location(db: Session, location_id: int):
    """Gets a specific location by its ID with eager loaded tags."""
    return db.query(Location).options(joinedload(Location.tags).joinedload(LocationTag.tag_type)).filter(Location.id == location_id).first()


def get_location_simple(db: Session, location_id: int):
    """Gets a specific location by its ID without relations."""
    return db.query(Location).filter(Location.id == location_id).first()


def get_locations_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    """Gets all locations belonging to a specific world."""
    return (
        db.query(Location)
        .filter(Location.world_id == world_id)
        .options(joinedload(Location.tags).joinedload(LocationTag.tag_type))
        .order_by(Location.name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_location_ids_in_world(db: Session, world_id: int) -> List[int]:
    """Gets IDs of all locations in a specific world."""
    return [loc.id for loc in db.query(Location.id).filter(Location.world_id == world_id).all()]


def _get_descendant_ids(db: Session, location_id: int, world_id: int) -> Set[int]:
    """Helper function to recursively get all descendant location IDs."""
    descendants = set()
    children = db.query(Location.id).filter(Location.world_id == world_id, Location.parent_location_id == location_id).all()
    child_ids = {child.id for child in children}
    descendants.update(child_ids)
    for child_id in child_ids:
        descendants.update(_get_descendant_ids(db, child_id, world_id))
    return descendants


def create_location(db: Session, location: LocationCreate):
    """Creates a new location."""
    # Optional: Validate parent_location_id belongs to the same world
    if location.parent_location_id:
        parent_location = get_location_simple(db, location.parent_location_id)
        if not parent_location or parent_location.world_id != location.world_id:
            raise HTTPException(status_code=400, detail="Parent location does not exist or belongs to a different world.")

    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, db_location: Location, location_in: LocationUpdate):
    """Updates a location, preventing circular dependencies."""
    update_data = location_in.dict(exclude_unset=True)

    # Check for circular dependency if parent_location_id is being set/changed
    if "parent_location_id" in update_data:
        new_parent_id = update_data["parent_location_id"]
        if new_parent_id is not None:
            # 1. Cannot set parent to self
            if new_parent_id == db_location.id:
                raise HTTPException(status_code=400, detail="Cannot set location's parent to itself.")

            # 2. Check if the new parent belongs to the same world
            parent_location = get_location_simple(db, new_parent_id)
            if not parent_location or parent_location.world_id != db_location.world_id:
                raise HTTPException(status_code=400, detail="Parent location does not exist or belongs to a different world.")

            # 3. Cannot set parent to a descendant
            descendant_ids = _get_descendant_ids(db, db_location.id, db_location.world_id)
            if new_parent_id in descendant_ids:
                raise HTTPException(status_code=400, detail="Cannot set location's parent to one of its descendants.")

    # Apply updates
    for key, value in update_data.items():
        setattr(db_location, key, value)

    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    # Return the updated object with potentially loaded relations if needed
    return get_location(db, db_location.id)


def delete_location(db: Session, db_location: Location):
    """Deletes a location. Assumes authorization check happened in the API layer."""
    # Optional: Handle children (e.g., set their parent_location_id to null or prevent deletion if children exist)
    # current behavior likely cascades or sets null based on DB constraints
    db.delete(db_location)
    db.commit()
    return db_location 