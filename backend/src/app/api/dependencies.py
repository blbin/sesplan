from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import Tuple, Optional

# Use absolute imports from the 'app' package
from app import crud, models
from app.db.session import get_db
from app.auth.auth import get_current_user
from app.models.user_campaign import CampaignRoleEnum
# Import pro ověření vlastníka světa
from app.models.world_user import RoleEnum as WorldRoleEnum, WorldUser 
from app.crud.crud_world_user import get_world_membership_with_role # Import our function

# Helper function to check campaign membership/role (GM)
async def verify_gm_permission(campaign_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership or membership.role != CampaignRoleEnum.GM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (GM required)")
    return membership # Můžeme vrátit členství pro případné další použití

# Závislost pro ověření vlastnictví světa
async def verify_world_owner(
    world_id: int, # world_id přijde z Path nebo z těla požadavku, ne přímo jako parametr Path() zde
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency to verify if the current user owns the world."""
    is_owner = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == world_id,
            WorldUser.user_id == current_user.id,
            WorldUser.role == WorldRoleEnum.OWNER
        )
        .first()
    )
    if not is_owner:
        world = crud.get_world(db, world_id=world_id)
        if not world:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions, must be world owner")
    # Úspěch - není potřeba nic vracet

# Sem můžeme v budoucnu přidat další sdílené závislosti/helpery pro API 

async def get_world_or_404(
    world_id: int = Path(..., description="ID světa"),
    db: Session = Depends(get_db),
) -> models.World:
    """Načte svět podle ID nebo vrátí 404."""
    db_world = crud.get_world(db, world_id=world_id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found")
    return db_world

# Zde by mohly být další závislosti, např. pro Campaign, Session atd.
# Příklad závislosti pro ověření GM kampaně:
async def get_campaign_and_verify_gm(
    campaign_id: int = Path(..., description="ID kampaně"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Campaign:
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    membership = await crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership or membership.role not in [crud.CampaignRoleEnum.GM]: # TODO: Použít enum správně
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="GM permissions required")

    return db_campaign

# Příklad závislosti pro ověření člena kampaně (GM nebo Player):
async def get_campaign_and_verify_member(
    campaign_id: int = Path(..., description="ID kampaně"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Campaign:
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    membership = await crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this campaign")

    return db_campaign

# Závislost pro získání session a ověření GM oprávnění (přes kampaň)
async def get_session_and_verify_gm(
    session_id: int = Path(..., description="ID sezení"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> models.Session:
    db_session = crud.get_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Ověření GM oprávnění přes nadřazenou kampaň
    await get_campaign_and_verify_gm(campaign_id=db_session.campaign_id, db=db, current_user=current_user)
    
    return db_session

# Závislost pro získání Journal a ověření vlastníka postavy (STARÁ - NEPOUŽÍVAT)
# async def get_journal_and_verify_owner(...)

# Závislost pro získání Journal Entry a ověření vlastníka postavy (STARÁ - NEPOUŽÍVAT)
# async def get_journal_entry_and_verify_owner(...)

# --- Nové závislosti pro Journal & Journal Entry --- 

async def get_journal_and_verify_permission(
    journal_id: int = Path(..., description="ID deníku"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Tuple[models.Journal, models.Character, Optional[models.WorldUser]]:
    """Dependency to get journal, its character, and user's world membership."""
    db_journal = crud.get_journal(db, journal_id=journal_id)
    if not db_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    
    db_character = crud.get_character(db, character_id=db_journal.character_id)
    if not db_character:
        # Should not happen if journal exists, but good practice
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character for this journal not found")

    # Get world membership (if any)
    world_membership = get_world_membership_with_role(db, world_id=db_character.world_id, user_id=current_user.id)

    return db_journal, db_character, world_membership

async def verify_journal_read_access(
    context: Tuple[models.Journal, models.Character, Optional[models.WorldUser]] = Depends(get_journal_and_verify_permission),
    current_user: models.User = Depends(get_current_user)
) -> models.Journal:
    """Verifies read access: Assigned user or World Owner/Admin."""
    db_journal, db_character, world_membership = context
    
    # Check if assigned user
    is_assigned_user = db_character.user_id == current_user.id
    # Check if world owner or admin
    is_world_manager = world_membership and world_membership.role in [WorldRoleEnum.OWNER, WorldRoleEnum.ADMIN]

    if not (is_assigned_user or is_world_manager):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this journal")
        
    return db_journal

async def verify_journal_write_access(
    context: Tuple[models.Journal, models.Character, Optional[models.WorldUser]] = Depends(get_journal_and_verify_permission)
) -> models.Journal:
    """Verifies write access: World Owner/Admin only."""
    db_journal, _, world_membership = context # Character not needed here
    
    # Check if world owner or admin
    is_world_manager = world_membership and world_membership.role in [WorldRoleEnum.OWNER, WorldRoleEnum.ADMIN]

    if not is_world_manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only world Owner or Admin can modify this journal")
        
    return db_journal

# --- Závislosti pro Journal Entries --- 

async def get_journal_entry_and_verify_permission(
    entry_id: int = Path(..., description="ID záznamu v deníku"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Tuple[models.JournalEntry, models.Character, Optional[models.WorldUser]]:
    """Dependency to get entry, its character, and user's world membership."""
    db_entry = crud.get_journal_entry(db, entry_id=entry_id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")

    # Get context via the parent journal
    try:
        _, db_character, world_membership = await get_journal_and_verify_permission(
            journal_id=db_entry.journal_id, db=db, current_user=current_user
        )
    except HTTPException as e:
         # If journal access check fails, re-raise but maybe adjust message
         # raise HTTPException(status_code=e.status_code, detail=f"Cannot access parent journal: {e.detail}")
         # Or just let the original exception propagate
         raise e

    return db_entry, db_character, world_membership

async def verify_journal_entry_read_access(
    context: Tuple[models.JournalEntry, models.Character, Optional[models.WorldUser]] = Depends(get_journal_entry_and_verify_permission),
    current_user: models.User = Depends(get_current_user)
) -> models.JournalEntry:
    """Verifies read access: Assigned user or World Owner/Admin."""
    db_entry, db_character, world_membership = context
    
    is_assigned_user = db_character.user_id == current_user.id
    is_world_manager = world_membership and world_membership.role in [WorldRoleEnum.OWNER, WorldRoleEnum.ADMIN]

    if not (is_assigned_user or is_world_manager):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this journal entry")
        
    return db_entry

async def verify_journal_entry_write_access(
    context: Tuple[models.JournalEntry, models.Character, Optional[models.WorldUser]] = Depends(get_journal_entry_and_verify_permission),
    current_user: models.User = Depends(get_current_user)
) -> models.JournalEntry:
    """Verifies write access: Assigned Character User OR World Owner/Admin."""
    db_entry, db_character, world_membership = context
    
    # Check if assigned user
    is_assigned_user = db_character.user_id == current_user.id
    # Check if world owner or admin
    is_world_manager = world_membership and world_membership.role in [WorldRoleEnum.OWNER, WorldRoleEnum.ADMIN]

    # Allow if either condition is met
    if not (is_assigned_user or is_world_manager):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character owner or world Owner/Admin required to modify this entry")
        
    return db_entry

# ----- Character Dependencies -----

async def get_character_or_404(
    character_id: int = Path(..., description="ID charakteru"),
    db: Session = Depends(get_db),
) -> models.Character:
    """Načte charakter podle ID nebo vrátí 404."""
    db_character = crud.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return db_character

async def verify_character_permission(
    character: models.Character = Depends(get_character_or_404), # Získáme charakter
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency to verify if the current user can modify the character (owner or world GM/Owner)."""
    # 1. Check if the current user is the character owner
    if character.user_id == current_user.id:
        return # Owner has permission

    # 2. Check if the current user is GM or Owner of the world the character belongs to
    world_membership = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == character.world_id,
            WorldUser.user_id == current_user.id,
            WorldUser.role.in_([WorldRoleEnum.OWNER, WorldRoleEnum.GM])
        )
        .first()
    )
    
    if world_membership:
        return # World Owner/GM has permission

    # If neither condition is met, raise forbidden
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to modify this character") 

# --- New Dependency/Helper Function ---

def check_world_membership(db: Session, world_id: int, user_id: int):
    """Checks if a user is a member of a world, raises 403 if not."""
    membership = db.query(WorldUser).filter(
        WorldUser.world_id == world_id,
        WorldUser.user_id == user_id
    ).first()
    
    if not membership:
        # If world exists but user is not a member, or if world doesn't exist
        # and membership is required anyway, always return 403.
        # The existence of the world itself should be checked by the calling endpoint if needed.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User does not have permission to access resources in this world"
        )
    # If membership exists, do nothing (permission granted for this check)

# --- End of New Dependency/Helper Function --- 