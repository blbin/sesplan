from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .. import models, schemas
from fastapi import HTTPException, status

def get_slot(db: Session, slot_id: int) -> Optional[models.SessionSlot]:
    """Get a session slot by its ID."""
    return db.query(models.SessionSlot).options(joinedload(models.SessionSlot.user_availabilities)).filter(models.SessionSlot.id == slot_id).first()

def get_slots_by_session(
    db: Session, session_id: int, skip: int = 0, limit: int = 100
) -> List[models.SessionSlot]:
    """Get all session slots for a specific session."""
    return (
        db.query(models.SessionSlot)
        .filter(models.SessionSlot.session_id == session_id)
        .order_by(models.SessionSlot.slot_from)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_session_slot(
    db: Session, slot_in: schemas.SessionSlotCreate, session_id: int
) -> models.SessionSlot:
    """Create a new session slot."""
    # Basic validation
    if slot_in.slot_to <= slot_in.slot_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot end time must be after start time."
        )
        
    db_slot = models.SessionSlot(
        **slot_in.model_dump(),
        session_id=session_id
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def update_session_slot(
    db: Session, db_slot: models.SessionSlot, slot_in: schemas.SessionSlotUpdate
) -> models.SessionSlot:
    """Update an existing session slot."""
    update_data = slot_in.model_dump(exclude_unset=True)

    # Validate times if both are provided in the update
    current_from = update_data.get('slot_from', db_slot.slot_from)
    current_to = update_data.get('slot_to', db_slot.slot_to)
    if current_to <= current_from:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot end time must be after start time."
        )

    for field, value in update_data.items():
        setattr(db_slot, field, value)

    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def delete_session_slot(db: Session, db_slot: models.SessionSlot) -> models.SessionSlot:
    """Delete a session slot."""
    # Cascade should handle deleting related UserAvailability entries
    db.delete(db_slot)
    db.commit()
    return db_slot 