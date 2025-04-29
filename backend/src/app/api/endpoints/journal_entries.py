from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional

from ... import crud, models, schemas
# Import RoleEnum directly
from ...models.world_user import RoleEnum 
from ...db.session import get_db
from ...auth.auth import get_current_user
# Import new dependencies
from ..dependencies import (
    verify_journal_read_access, 
    verify_journal_write_access,
    verify_journal_entry_read_access,
    verify_journal_entry_write_access,
    get_journal_and_verify_permission
)

# Prefix changed to avoid clash with journal routes
router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])

@router.post("/", response_model=schemas.JournalEntry, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    entry_in: schemas.JournalEntryCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create a new journal entry. Requires assigned user or world owner/admin."""
    # Verify access based on the parent journal's character
    try:
        # Get context (journal, character, membership)
        db_journal, db_character, world_membership = await get_journal_and_verify_permission(
            journal_id=entry_in.journal_id, db=db, current_user=current_user
        )
        
        # Check permissions: Assigned user OR World Owner/Admin
        is_assigned_user = db_character.user_id == current_user.id
        # Use the correctly imported RoleEnum
        is_world_manager = world_membership and world_membership.role in [RoleEnum.OWNER, RoleEnum.ADMIN]

        if not (is_assigned_user or is_world_manager):
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN, 
                 detail="Character owner or world Owner/Admin required to create entries in this journal"
             )

    except HTTPException as e:
        # Propagate potential 404 or other errors from get_journal_and_verify_permission
        raise e 

    entry = crud.create_journal_entry(db=db, entry_in=entry_in)
    return entry

# Get entries for a specific journal
@router.get("/by_journal/{journal_id}", response_model=List[schemas.JournalEntry])
async def read_entries_by_journal(
    # Use the dependency to verify read access to the parent journal
    parent_journal: models.Journal = Depends(verify_journal_read_access),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Retrieve entries for a specific journal. Requires assigned user or world owner/admin."""
    # We already verified read access via the dependency
    entries = crud.get_entries_by_journal(
        db, journal_id=parent_journal.id, skip=skip, limit=limit
    )
    return entries

@router.get("/{entry_id}", response_model=schemas.JournalEntry)
def read_journal_entry(
    # Use the new dependency for read access
    db_entry: models.JournalEntry = Depends(verify_journal_entry_read_access)
):
    """Get a specific journal entry by ID. Requires assigned user or world owner/admin."""
    return db_entry

@router.put("/{entry_id}", response_model=schemas.JournalEntry)
def update_journal_entry(
    *, # Enforce keyword-only arguments
    entry_in: schemas.JournalEntryUpdate,
    db: Session = Depends(get_db),
    # Use the new dependency for write access
    db_entry: models.JournalEntry = Depends(verify_journal_entry_write_access) 
):
    """Update a journal entry. Requires world owner/admin."""
    updated_entry = crud.update_journal_entry(db=db, db_entry=db_entry, entry_in=entry_in)
    return updated_entry

@router.delete("/{entry_id}", response_model=schemas.JournalEntry)
def delete_journal_entry(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    # Use the new dependency for write access
    db_entry: models.JournalEntry = Depends(verify_journal_entry_write_access) 
):
    """Delete a journal entry. Requires world owner/admin."""
    deleted_entry = crud.delete_journal_entry(db=db, db_entry=db_entry)
    return deleted_entry 