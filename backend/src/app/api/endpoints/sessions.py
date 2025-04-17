from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
# Import dependency for checking GM permission
from ..dependencies import verify_gm_permission 

router = APIRouter(tags=["sessions"])

# Dependency to get session and verify campaign membership (for read access)
async def get_session_and_verify_membership(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Session:
    db_session = crud.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    # Check if user is member of the parent campaign
    membership = crud.get_campaign_membership(db, campaign_id=db_session.campaign_id, user_id=current_user.id)
    if not membership:
        # Optionally check if campaign/world is public? Assuming sessions require membership.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this session's campaign")
    return db_session

# Dependency to get session and verify GM permission (for write access)
async def get_session_and_verify_gm(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Session:
    db_session = crud.get_session(db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    # Use verify_gm_permission for the parent campaign
    await verify_gm_permission(campaign_id=db_session.campaign_id, current_user=current_user, db=db)
    return db_session

@router.post("/", response_model=schemas.Session, status_code=status.HTTP_201_CREATED)
async def create_session(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    session_in: schemas.SessionCreate,
    current_user: models.User = Depends(get_current_user)
    # Removed gm_membership dependency from signature
):
    """Create a new session for a campaign. Requires GM role for the campaign."""
    # Verify GM permission for the target campaign inside the function body
    await verify_gm_permission(db=db, current_user=current_user, campaign_id=session_in.campaign_id)
    
    # If permission check passes, create the session
    session = crud.create_session(db=db, session_in=session_in)
    return session

@router.get("/by_campaign/{campaign_id}", response_model=List[schemas.Session])
def read_sessions_by_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve sessions for a specific campaign. Requires campaign membership."""
    # Check if user is member of the campaign
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership:
        # Optionally check if campaign/world is public?
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this campaign")
    
    sessions = crud.get_sessions_by_campaign(
        db, campaign_id=campaign_id, skip=skip, limit=limit
    )
    return sessions

@router.get("/{session_id}", response_model=schemas.Session)
def read_session(
    # Use dependency to get session and verify membership
    db_session: models.Session = Depends(get_session_and_verify_membership)
):
    """Get a specific session by ID. Requires membership in the parent campaign."""
    return db_session

@router.put("/{session_id}", response_model=schemas.Session)
def update_session(
    *, # Enforce keyword-only arguments
    session_in: schemas.SessionUpdate,
    db: Session = Depends(get_db),
    # Use dependency to get session and verify GM permission
    db_session: models.Session = Depends(get_session_and_verify_gm) 
):
    """Update a session. Requires GM role for the parent campaign."""
    updated_session = crud.update_session(db=db, db_session=db_session, session_in=session_in)
    return updated_session

@router.delete("/{session_id}", response_model=schemas.Session)
def delete_session(
    *, # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    # Use dependency to get session and verify GM permission
    db_session: models.Session = Depends(get_session_and_verify_gm)
):
    """Delete a session. Requires GM role for the parent campaign."""
    # Cascade should handle related SessionCharacter entries
    deleted_session = crud.delete_session(db=db, db_session=db_session)
    return deleted_session 