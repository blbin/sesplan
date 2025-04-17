from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas

def get_journal_entry(db: Session, entry_id: int) -> Optional[models.JournalEntry]:
    """Get a journal entry by its ID."""
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def get_entries_by_journal(
    db: Session, journal_id: int, skip: int = 0, limit: int = 100
) -> List[models.JournalEntry]:
    """Get all entries belonging to a specific journal."""
    return (
        db.query(models.JournalEntry)
        .filter(models.JournalEntry.journal_id == journal_id)
        .order_by(models.JournalEntry.created_at.desc()) # Optional: order by creation date
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_journal_entry(db: Session, entry_in: schemas.JournalEntryCreate) -> models.JournalEntry:
    """Create a new journal entry. Assumes journal_id is valid and ownership check happened elsewhere."""
    # TODO: Add check if journal_id exists?
    db_entry = models.JournalEntry(**entry_in.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def update_journal_entry(
    db: Session, db_entry: models.JournalEntry, entry_in: schemas.JournalEntryUpdate
) -> models.JournalEntry:
    """Update an existing journal entry. Assumes ownership check happened elsewhere."""
    update_data = entry_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_journal_entry(db: Session, db_entry: models.JournalEntry) -> models.JournalEntry:
    """Delete a journal entry. Assumes ownership check happened elsewhere."""
    db.delete(db_entry)
    db.commit()
    return db_entry # Or return {'id': db_entry.id, 'detail': 'Journal entry deleted'} 