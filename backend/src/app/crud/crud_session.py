from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas

def get_session(db: Session, session_id: int) -> Optional[models.Session]:
    """Get a session by its ID."""
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def get_sessions_by_campaign(
    db: Session, campaign_id: int, skip: int = 0, limit: int = 100
) -> List[models.Session]:
    """Get all sessions belonging to a specific campaign."""
    return (
        db.query(models.Session)
        .filter(models.Session.campaign_id == campaign_id)
        .order_by(models.Session.date_time.desc().nullslast(), models.Session.created_at.desc()) # Order by date, then creation
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_session(db: Session, session_in: schemas.SessionCreate) -> models.Session:
    """Create a new session. Assumes campaign_id is valid and ownership check happened elsewhere."""
    # TODO: Check if campaign_id exists?
    db_session = models.Session(**session_in.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(
    db: Session, db_session: models.Session, session_in: schemas.SessionUpdate
) -> models.Session:
    """Update an existing session. Assumes ownership check happened elsewhere."""
    update_data = session_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_session, key, value)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_session(db: Session, db_session: models.Session) -> models.Session:
    """Delete a session. Assumes ownership check happened elsewhere."""
    # Note: Relationships like SessionCharacter might need handling depending on cascade settings
    # The current model uses cascade="all, delete-orphan" for character_associations
    db.delete(db_session)
    db.commit()
    return db_session 