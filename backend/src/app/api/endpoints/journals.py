from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import verify_journal_read_access, verify_journal_write_access

router = APIRouter(tags=["journals"])

@router.get("/my-journals", response_model=List[schemas.Journal])
def read_my_journals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve journals for the current user's characters."""
    journals = crud.get_multi_by_owner(db=db, owner_id=current_user.id)
    return journals

@router.get("/{journal_id}", response_model=schemas.Journal)
def read_journal(
    # Use the new dependency for read access
    db_journal: models.Journal = Depends(verify_journal_read_access)
):
    """Get a specific journal by ID. Requires assigned user or world owner/admin."""
    return db_journal

@router.put("/{journal_id}", response_model=schemas.Journal)
def update_journal(
    *, # Enforce keyword-only arguments
    journal_in: schemas.JournalUpdate,
    db: Session = Depends(get_db),
    # Use the new dependency for write access
    db_journal: models.Journal = Depends(verify_journal_write_access) 
):
    """Update a journal (e.g., name, description). Requires world owner/admin."""
    updated_journal = crud.update_journal(db=db, db_journal=db_journal, journal_in=journal_in)
    return updated_journal

# Removed DELETE /{journal_id} endpoint (delete_journal - handled by cascade) 