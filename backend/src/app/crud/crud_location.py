from sqlalchemy.orm import Session
from ..models.location import Location
from ..schemas.location import LocationCreate, LocationUpdate


def get_location(db: Session, location_id: int):
    """Gets a specific location by its ID."""
    return db.query(Location).filter(Location.id == location_id).first()


def get_locations_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    """Gets all locations belonging to a specific world."""
    return (
        db.query(Location)
        .filter(Location.world_id == world_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_location(db: Session, location: LocationCreate):
    """Creates a new location."""
    # world_id is already in LocationCreate schema
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, db_location: Location, location_in: LocationUpdate):
    """Updates a location. Assumes authorization check happened in the API layer."""
    update_data = location_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_location, key, value)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, db_location: Location):
    """Deletes a location. Assumes authorization check happened in the API layer."""
    db.delete(db_location)
    db.commit()
    return db_location 