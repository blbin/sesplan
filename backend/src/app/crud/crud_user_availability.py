from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from .. import models, schemas
from fastapi import HTTPException, status

def get_user_availability(
    db: Session, user_id: int, slot_id: int
) -> Optional[models.UserAvailability]:
    """Get a specific user's availability for a specific slot."""
    return (
        db.query(models.UserAvailability)
        .filter(
            models.UserAvailability.user_id == user_id,
            models.UserAvailability.slot_id == slot_id,
        )
        .first()
    )

def get_availabilities_by_slot(
    db: Session, slot_id: int, skip: int = 0, limit: int = 100
) -> List[models.UserAvailability]:
    """Get all user availabilities for a specific slot."""
    return (
        db.query(models.UserAvailability)
        .filter(models.UserAvailability.slot_id == slot_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_availabilities_by_session(
    db: Session, session_id: int
) -> List[models.UserAvailability]:
    """Get all user availabilities across all slots for a specific session."""
    return (
        db.query(models.UserAvailability)
        .join(models.SessionSlot)
        .filter(models.SessionSlot.session_id == session_id)
        .all()
    )

def set_user_availability(
    db: Session, 
    slot: models.SessionSlot, 
    user_id: int, 
    availability_in: schemas.UserAvailabilityCreateUpdate
) -> models.UserAvailability:
    """Create or update a user's availability for a slot."""

    # Validate availability times against the slot times
    if (availability_in.available_from < slot.slot_from or 
        availability_in.available_to > slot.slot_to or 
        availability_in.available_to <= availability_in.available_from): # Redundant due to schema validation, but safe
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Availability times must be within the session slot boundaries and valid."
        )

    # Check if availability already exists for this user/slot
    db_availability = get_user_availability(db, user_id=user_id, slot_id=slot.id)

    if db_availability:
        # Update existing availability
        update_data = availability_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_availability, field, value)
        db.add(db_availability)
    else:
        # Create new availability
        db_availability = models.UserAvailability(
            **availability_in.model_dump(),
            user_id=user_id,
            slot_id=slot.id
        )
        db.add(db_availability)
        
    try:
        db.commit()
        db.refresh(db_availability)
    except IntegrityError: # Catch potential race conditions if unique constraint fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Availability record could not be created or updated. It might already exist."
        )
    
    return db_availability

def delete_user_availability(db: Session, user_id: int, slot_id: int) -> bool:
    """Delete a specific user's availability for a specific slot. Returns True if deleted, False otherwise."""
    db_availability = get_user_availability(db, user_id=user_id, slot_id=slot_id)
    if db_availability:
        db.delete(db_availability)
        db.commit()
        return True # Indicate successful deletion
    return False # Indicate nothing was deleted 