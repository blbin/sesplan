from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import sqlalchemy.orm

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
# Import helper function and RoleEnum
from ...crud.crud_world_user import get_world_membership_with_role
from ...models.world_user import RoleEnum

router = APIRouter()

# --- Helper for Permission Check --- Dependency maybe better later
def check_character_permission(
    db: Session,
    user: models.User,
    character: models.Character,
    allow_assigned: bool = True,
    roles_allowed: Optional[List[RoleEnum]] = None # Roles that grant access besides assigned user
) -> bool:
    """Checks if a user has permission for a character action."""
    if not character:
        return False # Or raise not found earlier
    
    # 1. Check if the user is the assigned user (if allowed for this action)
    if allow_assigned and character.user_id == user.id:
        return True
        
    # 2. Check world membership and role
    membership = get_world_membership_with_role(db, world_id=character.world_id, user_id=user.id)
    
    if membership and roles_allowed and membership.role in roles_allowed:
        return True
        
    return False

@router.post("/", response_model=schemas.Character)
def create_character(
    *,
    db: Session = Depends(get_db),
    character_in: schemas.CharacterCreate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Create new character. User must be a member of the world.
    """
    # CRUD funkce create_character nyní ověřuje členství ve světě
    character = crud.create_character(db=db, character_in=character_in, user_id=current_user.id)
    if not character:
        # CRUD vrátí None, pokud uživatel není členem světa nebo svět neexistuje
        raise HTTPException(status_code=403, detail="World not found or user is not a member")
    return character

@router.get("/", response_model=List[schemas.Character])
def read_characters(
    db: Session = Depends(get_db),
    world_id: Optional[int] = None, # Allow filtering by world
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve characters owned by the current user.
    Can be filtered by world_id.
    """
    if world_id:
        # Zde není potřeba ověřovat členství ve světě explicitně,
        # protože get_characters_by_world vrací jen postavy patřící current_user,
        # které mohou existovat jen ve světě, jehož je členem (ověřeno při create_character).
        characters = crud.get_characters_by_world(db, world_id=world_id, user_id=current_user.id, skip=skip, limit=limit)
    else:
        characters = crud.get_characters_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return characters

@router.get("/{character_id}", response_model=schemas.Character)
def read_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get character by ID. Allows assigned user or world OWNER/ADMIN.
    """
    db_character = (
        db.query(models.Character)
        .options(
            sqlalchemy.orm.selectinload(models.Character.tags)
            .joinedload(models.CharacterTag.tag_type)
        )
        .filter(models.Character.id == character_id)
        .first()
    )
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check permissions: Assigned user OR Owner/Admin
    if not check_character_permission(
        db, current_user, db_character, 
        allow_assigned=True, 
        roles_allowed=[RoleEnum.OWNER, RoleEnum.ADMIN]
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return db_character

@router.put("/{character_id}", response_model=schemas.Character)
def update_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    character_in: schemas.CharacterUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a character.
    - Assigned user can update name and description.
    - World OWNER or ADMIN can update name, description, tags, and assigned user.
    """
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check basic permission: Assigned user OR Owner/Admin
    if not check_character_permission(
        db, current_user, db_character, 
        allow_assigned=True, # Allow assigned user
        roles_allowed=[RoleEnum.OWNER, RoleEnum.ADMIN]
    ):
        # This error shouldn't be reached if the user is assigned or manager, 
        # but kept for safety.
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if the user is Owner/Admin for full update rights
    membership = get_world_membership_with_role(db, world_id=db_character.world_id, user_id=current_user.id)
    is_world_manager = membership and membership.role in [RoleEnum.OWNER, RoleEnum.ADMIN]

    # Prepare data for update, respecting permissions
    update_data = character_in.dict(exclude_unset=True)

    if not is_world_manager:
        # If user is only the assigned user, restrict updates
        allowed_keys = {'name', 'description'}
        # Remove fields the assigned user cannot change
        update_data = {k: v for k, v in update_data.items() if k in allowed_keys}
        if not update_data:
            # No allowed fields were provided for update
            # Return the character without changes or raise a 400 Bad Request?
            # Let's return the character as no update is performed.
             # Alternatively, could raise HTTPException(status_code=400, detail="No updatable fields provided for assigned user.")
             return db_character # Or maybe raise 400?
    
    # Create a new CharacterUpdate schema instance with filtered data
    # This ensures that validation still happens on the data we intend to update
    try:
         # Use exclude_none=True as well if None values should not overwrite existing ones unless explicitly provided
         # However, for user_id, we might want to allow setting to None by Owner/Admin
         filtered_character_in = schemas.CharacterUpdate(**update_data) 
    except Exception as e:
         # Handle potential validation errors if filtering resulted in invalid state (unlikely here)
         raise HTTPException(status_code=400, detail=f"Invalid update data after permission filtering: {e}")

    # Perform the update with filtered data
    character = crud.update_character(db=db, db_character=db_character, character_in=filtered_character_in)
    return character

@router.delete("/{character_id}", response_model=schemas.Character)
def delete_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a character. Requires world OWNER or ADMIN role.
    """
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check permissions: Owner/Admin required for delete
    if not check_character_permission(
        db, current_user, db_character, 
        allow_assigned=False, 
        roles_allowed=[RoleEnum.OWNER, RoleEnum.ADMIN]
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions (Owner/Admin required)")

    character = crud.delete_character(db=db, db_character=db_character)
    return character

@router.patch("/{character_id}/assign_user", response_model=schemas.Character)
def assign_user_to_character(
    *,
    db: Session = Depends(get_db),
    character_id: int,
    assignment_in: schemas.CharacterAssignUser,
    current_user: models.User = Depends(get_current_user)
):
    """
    Assign a user to a character or unassign them.
    Requires world OWNER or ADMIN role.
    The target user must be a member of a campaign within the character's world.
    """
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    # --- Authorization Check --- 
    # Check if the current user is Owner or Admin of the world
    membership = get_world_membership_with_role(db, world_id=db_character.world_id, user_id=current_user.id)
    if not membership or membership.role not in [RoleEnum.OWNER, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Only world Owner or Admin can assign characters")

    target_user_id = assignment_in.user_id
    
    # --- Validation for Assignment (if user_id is not None) ---
    if target_user_id is not None:
        # Check if the target user exists
        target_user = crud.get_user(db, user_id=target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Target user with id {target_user_id} not found")

        # Check if the target user is in any campaign within this world
        campaigns_in_world = crud.get_campaigns_by_world(db, world_id=db_character.world_id)
        campaign_ids_in_world = {campaign.id for campaign in campaigns_in_world}
        
        is_user_in_relevant_campaign = (
            db.query(models.UserCampaign)
            .filter(
                models.UserCampaign.user_id == target_user_id,
                models.UserCampaign.campaign_id.in_(campaign_ids_in_world)
            )
            .first()
        )
        
        if not is_user_in_relevant_campaign:
            raise HTTPException(
                status_code=400, 
                detail=f"User {target_user_id} is not part of any campaign in world {db_character.world_id}"
            )

    # --- Perform Assignment --- 
    updated_character = crud.assign_user_to_character(
        db=db, 
        db_character=db_character, 
        user_id=target_user_id
    )
    return updated_character 