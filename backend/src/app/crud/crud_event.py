from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas

def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    """Získá jednu událost podle ID."""
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events_by_world(
    db: Session, world_id: int, skip: int = 0, limit: int = 100
) -> List[models.Event]:
    """Získá všechny události patřící danému světu."""
    return (
        db.query(models.Event)
        .filter(models.Event.world_id == world_id)
        .order_by(models.Event.date.asc().nullslast(), models.Event.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_event(db: Session, event_in: schemas.EventCreate, world_id: int) -> models.Event:
    """Vytvoří novou událost."""
    db_event = models.Event(**event_in.dict(), world_id=world_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(
    db: Session, db_event: models.Event, event_in: schemas.EventUpdate
) -> models.Event:
    """Aktualizuje existující událost."""
    update_data = event_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, db_event: models.Event) -> models.Event:
    """Smaže událost."""
    db.delete(db_event)
    db.commit()
    return db_event 