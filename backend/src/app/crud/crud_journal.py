from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas

def get_journal(db: Session, journal_id: int) -> Optional[models.Journal]:
    """Get a journal by its ID."""
    return db.query(models.Journal).filter(models.Journal.id == journal_id).first()

def update_journal(
    db: Session, db_journal: models.Journal, journal_in: schemas.JournalUpdate
) -> models.Journal:
    """Update an existing journal. Assumes ownership check happened elsewhere."""
    update_data = journal_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_journal, key, value)
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal

def get_multi_by_owner(db: Session, owner_id: int) -> List[models.Journal]:
    """Get all journals belonging to characters owned by a specific user."""
    return (
        db.query(models.Journal)
        .join(models.Character, models.Journal.character_id == models.Character.id)
        .filter(models.Character.user_id == owner_id)
        .all()
    ) 