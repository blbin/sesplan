from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from datetime import datetime

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from ..dependencies import verify_campaign_membership, verify_gm_for_session 

# Define router. We will include it under /sessions/{session_id} in the main API router
router = APIRouter()

# --- Dependency to get Session Slot --- 
def get_session_slot( 
    slot_id: Annotated[int, Path(description="The ID of the session slot")],
    db: Session = Depends(get_db)
) -> models.SessionSlot:
    db_slot = crud.get_slot(db, slot_id=slot_id)
    if not db_slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session slot not found")
    return db_slot

# --- Session Slot Endpoints (GM only for write operations) --- 

@router.post(
    "/slots", 
    response_model=schemas.SessionSlot, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_gm_for_session)] # Use new dependency
)
def create_slot(
    session_id: Annotated[int, Path(description="The ID of the session to add the slot to")],
    slot_in: schemas.SessionSlotCreate,
    db: Session = Depends(get_db),
    # current_user is implicitly checked by verify_gm_for_session
):
    """Create a new availability slot for a session. Requires GM permission for the campaign."""
    # Session existence and GM permission checked by dependency
    # db_session = crud.get_session(db, session_id=session_id) # No longer needed here
    # if not db_session:
    #      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return crud.create_session_slot(db=db, slot_in=slot_in, session_id=session_id)

@router.get(
    "/slots", 
    response_model=List[schemas.SessionSlot],
    dependencies=[Depends(verify_campaign_membership)] # Membership check - OK
)
def read_slots(
    session_id: Annotated[int, Path(description="The ID of the session to get slots from")],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve all availability slots for a session. Requires campaign membership."""
    # Permission already checked by dependency
    slots = crud.get_slots_by_session(db, session_id=session_id, skip=skip, limit=limit)
    return slots

@router.put(
    "/slots/{slot_id}", 
    response_model=schemas.SessionSlot,
    dependencies=[Depends(verify_gm_for_session)] # Use new dependency
)
def update_slot(
    session_id: Annotated[int, Path(description="The ID of the session the slot belongs to (for permission check)")],
    slot_in: schemas.SessionSlotUpdate,
    db_slot: models.SessionSlot = Depends(get_session_slot),
    db: Session = Depends(get_db),
    # current_user checked by dependency
):
    """Update an availability slot. Requires GM permission."""
    # Check if the slot actually belongs to the session from the path parameter
    # The dependency verify_gm_for_session only checks permission based on session_id
    # It doesn't guarantee the slot_id belongs to *that* session.
    if db_slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to the specified session")
    return crud.update_session_slot(db=db, db_slot=db_slot, slot_in=slot_in)

@router.delete(
    "/slots/{slot_id}", 
    response_model=schemas.SessionSlot, # Return the deleted slot
    dependencies=[Depends(verify_gm_for_session)] # Use new dependency
)
def delete_slot(
    session_id: Annotated[int, Path(description="The ID of the session the slot belongs to (for permission check)")],
    db_slot: models.SessionSlot = Depends(get_session_slot),
    db: Session = Depends(get_db),
    # current_user checked by dependency
):
    """Delete an availability slot. Requires GM permission."""
    if db_slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to the specified session")
    return crud.delete_session_slot(db=db, db_slot=db_slot)

# --- User Availability Endpoints (Players/Members) ---

@router.put(
    "/slots/{slot_id}/availabilities/me", 
    response_model=schemas.UserAvailability,
    dependencies=[Depends(verify_campaign_membership)] # Membership check - OK
)
def set_my_availability(
    session_id: Annotated[int, Path(description="The ID of the session (for permission check)")],
    slot_id: Annotated[int, Path(description="The ID of the slot to set availability for")],
    availability_in: schemas.UserAvailabilityCreateUpdate,
    db_slot: models.SessionSlot = Depends(get_session_slot), # Get the slot to validate against
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Set or update the current user's availability for a specific slot. Requires campaign membership."""
    # Ensure the slot belongs to the session mentioned in the path
    if db_slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to the specified session")
    # Ensure slot_id from path matches the fetched slot's id
    if db_slot.id != slot_id: 
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path slot ID mismatch")

    return crud.set_user_availability(
        db=db, 
        slot=db_slot, 
        user_id=current_user.id, 
        availability_in=availability_in
    )

@router.delete(
    "/slots/{slot_id}/availabilities/me", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_campaign_membership)]
)
def delete_my_availability(
    session_id: Annotated[int, Path(description="The ID of the session (for permission check)")],
    slot_id: Annotated[int, Path(description="The ID of the slot to delete availability from")],
    time_from: Optional[datetime] = None,
    time_to: Optional[datetime] = None,
    db_slot: models.SessionSlot = Depends(get_session_slot), # Ensure slot exists
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete the current user's availability for a specific slot.
    
    Pokud jsou zadány parametry time_from a time_to, budou smazány všechny záznamy,
    které se s daným časovým intervalem překrývají. Jinak bude smazána jedna dostupnost.
    
    Requires campaign membership.
    """
    if db_slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to the specified session")
    if db_slot.id != slot_id: 
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path slot ID mismatch")

    # Kontrola časové validity, pokud jsou zadány časové parametry
    if time_from is not None and time_to is not None:
        if time_from >= time_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="time_from must be before time_to"
            )
        
        # Kontrola, že časový interval je v rámci slotu
        if time_from < db_slot.slot_from or time_to > db_slot.slot_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time interval must be within the session slot boundaries"
            )

    # Call the updated CRUD function which now supports interval-based deletion
    deleted = crud.delete_user_availability(
        db=db, 
        user_id=current_user.id, 
        slot_id=slot_id,
        time_from=time_from,
        time_to=time_to
    )

    return None # Return 204 No Content

@router.get(
    "/slots/{slot_id}/availabilities", 
    response_model=List[schemas.UserAvailability],
    dependencies=[Depends(verify_campaign_membership)] # Membership check - OK
)
def read_slot_availabilities(
    session_id: Annotated[int, Path(description="The ID of the session (for permission check)")],
    slot_id: Annotated[int, Path(description="The ID of the slot to get availabilities from")],
    db_slot: models.SessionSlot = Depends(get_session_slot), # Ensure slot exists
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Get all user availabilities for a specific slot. Requires campaign membership."""
    if db_slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to the specified session")
    if db_slot.id != slot_id: 
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path slot ID mismatch")
    
    availabilities = crud.get_availabilities_by_slot(db, slot_id=slot_id, skip=skip, limit=limit)
    return availabilities

@router.get(
    "/availabilities", 
    response_model=List[schemas.UserAvailability],
    dependencies=[Depends(verify_campaign_membership)] # Membership check - OK
)
def read_all_session_availabilities(
    session_id: Annotated[int, Path(description="The ID of the session to get all availabilities from")],
    db: Session = Depends(get_db),
):
    """Get all user availabilities across all slots for a specific session. Requires campaign membership."""
    # Permission dependency already checked
    # Session existence check is handled by verify_campaign_membership dependency
    # db_session = crud.get_session(db, session_id=session_id)
    # if not db_session:
    #      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
         
    all_availabilities = crud.get_all_availabilities_by_session(db, session_id=session_id)
    return all_availabilities 