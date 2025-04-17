from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Use absolute imports from the 'app' package
from app import crud, models
from app.db.session import get_db
from app.auth.auth import get_current_user
from app.models.user_campaign import CampaignRoleEnum

# Helper function to check campaign membership/role (GM)
async def verify_gm_permission(campaign_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership or membership.role != CampaignRoleEnum.GM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (GM required)")
    return membership # Můžeme vrátit členství pro případné další použití

# Sem můžeme v budoucnu přidat další sdílené závislosti/helpery pro API 

async def get_journal_and_verify_owner(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Journal:
    """Dependency to get a journal by ID and verify the current user owns the parent character."""
    db_journal = crud.get_journal(db, journal_id=journal_id)
    if not db_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    # Fetch the character associated with the journal
    db_character = crud.get_character(db, character_id=db_journal.character_id)
    if not db_character or db_character.user_id != current_user.id:
        # Either character doesn't exist or user doesn't own it
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db_journal

async def get_journal_entry_and_verify_owner(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.JournalEntry:
    """Dependency to get a journal entry by ID and verify the current user owns the parent character."""
    db_entry = crud.get_journal_entry(db, entry_id=entry_id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    # Fetch the parent journal
    db_journal = crud.get_journal(db, journal_id=db_entry.journal_id)
    if not db_journal:
        # This should ideally not happen if DB constraints are set, but check anyway
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent journal not found")
    # Fetch the character associated with the journal
    db_character = crud.get_character(db, character_id=db_journal.character_id)
    if not db_character or db_character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db_entry 