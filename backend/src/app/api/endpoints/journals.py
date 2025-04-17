from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import get_journal_and_verify_owner # Import the dependency

router = APIRouter(tags=["journals"])

# Removed POST / endpoint (create_journal)
# Removed GET /by_character/{character_id} endpoint (read_journals_by_character)

@router.get("/{journal_id}", response_model=schemas.Journal)
def read_journal(
    # Use the dependency to get journal and verify ownership
    db_journal: models.Journal = Depends(get_journal_and_verify_owner)
):
    """Get a specific journal by ID. Requires ownership of the parent character."""
    return db_journal

@router.put("/{journal_id}", response_model=schemas.Journal)
def update_journal(
    *, # Enforce keyword-only arguments
    journal_in: schemas.JournalUpdate,
    db: Session = Depends(get_db),
    db_journal: models.Journal = Depends(get_journal_and_verify_owner) # Get/verify journal
):
    """Update a journal (e.g., name, description). Requires ownership of the parent character."""
    updated_journal = crud.update_journal(db=db, db_journal=db_journal, journal_in=journal_in)
    return updated_journal

# Removed DELETE /{journal_id} endpoint (delete_journal - handled by cascade) 