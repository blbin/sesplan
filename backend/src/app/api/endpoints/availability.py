from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.schemas.availability import AvailabilityBase
from app.api import dependencies as deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Availability])
def read_session_availabilities(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all availabilities for a specific session.
    No permission check here, anyone can see who is available for a session.
    Adjust if different privacy is needed.
    """
    session = crud.get_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    availabilities = crud.get_availabilities_by_session(
        db=db, session_id=session_id, skip=skip, limit=limit
    )
    return availabilities

@router.get("/me", response_model=List[schemas.Availability])
def read_my_session_availability(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get the current user's availability records for a specific session.
    Returns an empty list if none are found.
    """
    session = crud.get_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    availabilities = crud.get_availability_by_user_and_session(
        db=db, user_id=current_user.id, session_id=session_id
    )
    return availabilities

@router.put("/me", response_model=List[schemas.Availability])
def set_my_session_availability(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    availabilities_in: List[AvailabilityBase],
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Set the current user's availability for a specific session.
    Replaces any existing availability records for the user/session with the provided ones.
    """
    session = crud.get_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    updated_availabilities = crud.set_user_session_availability(
        db=db, 
        user_id=current_user.id, 
        session_id=session_id, 
        availabilities_in=availabilities_in
    )
    return updated_availabilities

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_session_availability(
    *,
    db: Session = Depends(deps.get_db),
    session_id: int,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Delete all of the current user's availability records for a specific session.
    """
    session = crud.get_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    crud.delete_all_user_session_availability(db=db, user_id=current_user.id, session_id=session_id)
    return None 