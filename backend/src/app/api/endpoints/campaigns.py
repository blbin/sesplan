from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
from . import campaign_invites # Import the campaign invites endpoints
from ...models.world_user import RoleEnum as WorldRoleEnum # Enum pro role ve světě
from ..dependencies import verify_gm_permission

router = APIRouter()

# Helper function to check world ownership
async def verify_world_owner(world_id: int, user_id: int, db: Session = Depends(get_db)):
    membership = db.query(models.WorldUser).filter(
        models.WorldUser.world_id == world_id,
        models.WorldUser.user_id == user_id,
        models.WorldUser.role == WorldRoleEnum.OWNER
    ).first()
    if not membership:
        # Svět nenalezen nebo uživatel není vlastník
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="World not found or not owned by user")
    return membership

@router.post("/", response_model=schemas.Campaign)
async def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_user)
):
    """Create new campaign. User must be OWNER of the world. Creator becomes GM."""
    # Ověření vlastnictví světa pomocí helper funkce
    await verify_world_owner(campaign_in.world_id, current_user.id, db)

    # CRUD funkce se postará o vytvoření kampaně a přiřazení GM role
    campaign = crud.create_campaign(db=db, campaign=campaign_in, creator_id=current_user.id)
    if not campaign:
        # CRUD by neměla vrátit None, pokud prošlo ověření světa, ale pro jistotu
        raise HTTPException(status_code=500, detail="Failed to create campaign")
    return campaign

@router.get("/", response_model=List[schemas.Campaign])
async def read_campaigns(
    db: Session = Depends(get_db),
    world_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """Retrieve campaigns. If world_id is provided, user must be member of the world."""
    if world_id:
        # Ověření, zda je uživatel členem světa
        world_membership = db.query(models.WorldUser).filter(
            models.WorldUser.world_id == world_id,
            models.WorldUser.user_id == current_user.id
        ).first()
        if not world_membership:
             # Check if world is public first? Assuming private worlds require membership
             world = crud.get_world(db, world_id=world_id)
             if not world or not world.is_public:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found or access denied")
             # If public, allow fetching campaigns (they might be filtered later by campaign membership)

        # Vrátí kampaně daného světa (bez ohledu na členství v kampani zde)
        campaigns = crud.get_campaigns_by_world(db, world_id=world_id, skip=skip, limit=limit)
    else:
        # Vrátí všechny kampaně, kde je uživatel GM
        campaigns = crud.get_campaigns_by_owner(db, user_id=current_user.id, skip=skip, limit=limit)
    return campaigns

@router.get("/{campaign_id}", response_model=schemas.Campaign)
async def read_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """Get campaign by ID. Requires membership in the campaign."""
    campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Ověření členství v kampani
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership:
        # Mohli bychom zde také zkontrolovat, zda svět kampaně není veřejný,
        # ale pro detail kampaně dává smysl vyžadovat členství.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to access this campaign")

    return campaign

@router.put("/{campaign_id}", response_model=schemas.Campaign)
async def update_campaign(
    *,
    campaign_id: int,
    campaign_in: schemas.CampaignUpdate,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """Update a campaign. Requires GM role."""
    # gm_membership již obsahuje načtenou kampaň (nepřímo), ale pro jistotu načteme znovu
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
         raise HTTPException(status_code=404, detail="Campaign not found") # Mělo by být ošetřeno už ve verify_gm_permission

    # CRUD funkce provede update
    campaign = crud.update_campaign(db=db, db_campaign=db_campaign, campaign_in=campaign_in)
    return campaign

@router.delete("/{campaign_id}", response_model=schemas.Campaign)
async def delete_campaign(
    *,
    campaign_id: int,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """Delete a campaign. Requires GM role."""
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # CRUD funkce provede smazání
    campaign = crud.delete_campaign(db=db, db_campaign=db_campaign)
    return campaign

# --- Member Management Router ---
member_router = APIRouter()

@member_router.get("/", response_model=List[schemas.UserCampaignRead])
async def read_campaign_members(
    *,
    campaign_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # Verify membership instead of GM role
    current_user: models.User = Depends(get_current_user) 
):
    """Retrieve members of a campaign. Requires campaign membership."""
    # Check if the current user is a member of the campaign
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership:
        # Optional: Check if campaign/world is public?
        # For listing members, requiring membership seems reasonable.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this campaign")
        
    # If user is a member, fetch all members
    members = crud.get_campaign_members(db, campaign_id=campaign_id, skip=skip, limit=limit)
    return members

@member_router.put("/{user_id}", response_model=schemas.UserCampaignRead)
async def update_member_role(
    *,
    campaign_id: int,
    user_id: int,
    role_update: schemas.UserCampaignUpdate,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """Update the role of a campaign member. Only GMs can update roles."""
    updated_membership = crud.update_campaign_member_role(
        db, campaign_id=campaign_id, user_id=user_id, role_update=role_update
    )
    if updated_membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    if isinstance(updated_membership, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_membership)

    # Načíst znovu s detaily uživatele pro response_model
    final_membership = (
        db.query(models.UserCampaign)
        .options(joinedload(models.UserCampaign.user))
        .filter(models.UserCampaign.id == updated_membership.id)
        .first()
    )
    # Handle case where final_membership might be None (shouldn't happen if update worked)
    if not final_membership:
        raise HTTPException(status_code=500, detail="Failed to reload membership after update")
    return final_membership

@member_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    *,
    campaign_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """Remove a member from a campaign. Only GMs can remove members."""
    if gm_membership.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GM cannot remove themselves via this endpoint. Delete the campaign instead or assign another GM.")

    result = crud.remove_campaign_member(db, campaign_id=campaign_id, user_id_to_remove=user_id)

    if result is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

# Zahrnutí routeru pro členy
router.include_router(
    member_router,
    prefix="/{campaign_id}/members",
    tags=["campaign-members"]
)

# Zahrnutí routeru pro pozvánky specifické pro kampaň
router.include_router(
    campaign_invites.campaign_specific_invite_router,
    prefix="/{campaign_id}/invites",
    tags=["campaign-invites"]
) 