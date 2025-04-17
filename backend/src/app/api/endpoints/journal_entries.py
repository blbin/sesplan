from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
# Import both dependency functions
from ..dependencies import (
    get_journal_and_verify_owner,
    get_journal_entry_and_verify_owner
)

# Prefix changed to avoid clash with journal routes
router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])

@router.post("/", response_model=schemas.JournalEntry, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    entry_in: schemas.JournalEntryCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create a new journal entry. Requires ownership of the parent journal's character."""
    # Verify user owns the character associated with the parent journal
    parent_journal = crud.get_journal(db, journal_id=entry_in.journal_id)
    if not parent_journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent journal with id {entry_in.journal_id} not found.",
        )
    parent_character = crud.get_character(db, character_id=parent_journal.character_id)
    if not parent_character or parent_character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create an entry for this journal.",
        )

    entry = crud.create_journal_entry(db=db, entry_in=entry_in)
    return entry

# Get entries for a specific journal
@router.get("/by_journal/{journal_id}", response_model=List[schemas.JournalEntry])
def read_entries_by_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # Verify ownership of the journal first
    parent_journal: models.Journal = Depends(get_journal_and_verify_owner) 
):
    """Retrieve entries for a specific journal. Requires ownership of the journal."""
    # We already verified ownership via the dependency
    entries = crud.get_entries_by_journal(
        db, journal_id=parent_journal.id, skip=skip, limit=limit
    )
    return entries

@router.get("/{entry_id}", response_model=schemas.JournalEntry)
def read_journal_entry(
    # Use the dependency to get entry and verify ownership
    db_entry: models.JournalEntry = Depends(get_journal_entry_and_verify_owner)
):
    """Get a specific journal entry by ID. Requires ownership of the parent journal's character."""
    return db_entry

@router.put("/{entry_id}", response_model=schemas.JournalEntry)
def update_journal_entry(
    *, # Enforce keyword-only arguments
    entry_in: schemas.JournalEntryUpdate,
    db: Session = Depends(get_db),
    # Get/verify entry using dependency
    db_entry: models.JournalEntry = Depends(get_journal_entry_and_verify_owner) 
):
    """Update a journal entry. Requires ownership of the parent journal's character."""
    updated_entry = crud.update_journal_entry(db=db, db_entry=db_entry, entry_in=entry_in)
    return updated_entry

@router.delete("/{entry_id}", response_model=schemas.JournalEntry)
def delete_journal_entry(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    # Get/verify entry using dependency
    db_entry: models.JournalEntry = Depends(get_journal_entry_and_verify_owner) 
):
    """Delete a journal entry. Requires ownership of the parent journal's character."""
    deleted_entry = crud.delete_journal_entry(db=db, db_entry=db_entry)
    return deleted_entry 