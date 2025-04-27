from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime

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
    """Create a user's availability for a slot.
    Allows multiple entries per user/slot, but prevents overlapping time intervals.
    """

    # Validate availability times against the slot times
    if (
        availability_in.available_from < slot.slot_from or 
        availability_in.available_to > slot.slot_to or 
        availability_in.available_to <= availability_in.available_from
    ): 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Availability times must be within the session slot boundaries and valid."
        )

    # Get all existing availability for this user/slot
    existing_availabilities = (
        db.query(models.UserAvailability)
        .filter(
            models.UserAvailability.user_id == user_id,
            models.UserAvailability.slot_id == slot.id
        )
        .all()
    )
    
    # Check for overlap with existing intervals
    new_start = availability_in.available_from
    new_end = availability_in.available_to
    for existing in existing_availabilities:
        # Overlap condition: (StartA < EndB) and (EndA > StartB)
        if new_start < existing.available_to and new_end > existing.available_from:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"New availability interval from {new_start} to {new_end} overlaps with existing interval from {existing.available_from} to {existing.available_to}."
            )

    # No overlap found, create the new availability record
    new_availability = models.UserAvailability(
        **availability_in.model_dump(),
        user_id=user_id,
        slot_id=slot.id
    )
    
    db.add(new_availability)
    try:
        db.commit()
        db.refresh(new_availability)
        return new_availability
    except IntegrityError: # Should not happen often now, but keep for safety
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # Changed from 409 as unique constraint is gone
            detail="Failed to save availability record due to an unexpected database error."
        )

def delete_user_availability(db: Session, user_id: int, slot_id: int, time_from: Optional[datetime] = None, time_to: Optional[datetime] = None) -> bool:
    """Delete a specific user's availability for a specific slot.
    
    Args:
        db: Database session
        user_id: ID uživatele
        slot_id: ID slotu
        time_from: Volitelný začátek intervalu pro smazání
        time_to: Volitelný konec intervalu pro smazání
        
    Pokud jsou time_from a time_to zadány, budou smazány všechny záznamy,
    které se s tímto intervalem překrývají. Jinak bude smazán jeden konkrétní záznam.
    
    Returns:
        True pokud byl alespoň jeden záznam smazán, jinak False
    """
    if time_from is not None and time_to is not None:
        # Smazání podle časového intervalu
        overlapping_records = (
            db.query(models.UserAvailability)
            .filter(
                models.UserAvailability.user_id == user_id,
                models.UserAvailability.slot_id == slot_id,
                models.UserAvailability.available_from < time_to,  # Začátek záznamu je před koncem intervalu
                models.UserAvailability.available_to > time_from,  # Konec záznamu je po začátku intervalu
            )
            .all()
        )
        
        if not overlapping_records:
            return False
            
        for record in overlapping_records:
            db.delete(record)
        
        db.commit()
        return True
    else:
        # Původní implementace - smazání jednoho záznamu
        db_availability = get_user_availability(db, user_id=user_id, slot_id=slot_id)
        if db_availability:
            db.delete(db_availability)
            db.commit()
            return True
        return False 