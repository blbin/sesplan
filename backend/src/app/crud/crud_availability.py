from sqlalchemy.orm import Session
from .. import models, schemas
from ..schemas.availability import AvailabilityBase
from datetime import datetime
from typing import List, Optional

def get_availability(db: Session, availability_id: int) -> Optional[models.Availability]:
    """Gets a single availability record by its ID."""
    return db.query(models.Availability).filter(models.Availability.id == availability_id).first()

def get_availability_by_user_and_session(db: Session, user_id: int, session_id: int) -> List[models.Availability]:
    """Gets all availability records for a specific user and session."""
    return db.query(models.Availability).filter(
        models.Availability.user_id == user_id,
        models.Availability.session_id == session_id
    ).all()

def get_availabilities_by_session(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[models.Availability]:
    """Gets all availability records for a specific session."""
    return db.query(models.Availability).filter(models.Availability.session_id == session_id).offset(skip).limit(limit).all()

def create_availability(db: Session, availability: schemas.AvailabilityCreate, user_id: int, session_id: int) -> models.Availability:
    """Creates a new availability record for a user and session."""
    db_availability = models.Availability(
        **availability.dict(),
        user_id=user_id,
        session_id=session_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

def set_user_session_availability(db: Session, user_id: int, session_id: int, availabilities_in: List[AvailabilityBase]) -> List[models.Availability]:
    """
    Deletes all existing availability for the user/session and creates new ones based on the input list.
    """
    # 1. Delete existing availability for the user in this session
    db.query(models.Availability).filter(
        models.Availability.user_id == user_id,
        models.Availability.session_id == session_id
    ).delete(synchronize_session=False) # Use synchronize_session=False for potentially better performance

    # 2. Create new availability records
    new_availabilities = []
    for availability_in in availabilities_in:
        db_availability = models.Availability(
            **availability_in.dict(),
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_availability)
        new_availabilities.append(db_availability)

    db.commit()
    # Refresh each new object to get IDs etc.
    for db_obj in new_availabilities:
        db.refresh(db_obj)
    return new_availabilities

def delete_all_user_session_availability(db: Session, user_id: int, session_id: int) -> int:
    """
    Deletes all availability records for a specific user and session.
    Returns the number of deleted records.
    """
    deleted_count = db.query(models.Availability).filter(
        models.Availability.user_id == user_id,
        models.Availability.session_id == session_id
    ).delete(synchronize_session=False)
    db.commit()
    return deleted_count
