from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user
# Import the dependency
from ..dependencies import verify_gm_permission
# Import enum for manual check fallback if needed
from ...models.user_campaign import CampaignRoleEnum

# Použijeme samostatný router pro invite operace, které nejsou přímo pod /campaigns/{id}
# Např. přijetí pozvánky pomocí tokenu
invite_router = APIRouter()
# Router pro operace vázané na konkrétní kampaň
campaign_specific_invite_router = APIRouter()

@campaign_specific_invite_router.post("/", response_model=schemas.CampaignInvite, status_code=status.HTTP_201_CREATED)
async def create_campaign_invite(
    *,
    campaign_id: int,
    invite_in: schemas.CampaignInviteCreate,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """
    Create a new invite for a campaign. Requires GM role.
    """
    # Authorization checked by verify_gm_permission dependency
    invite = crud.create_campaign_invite(db=db, campaign_id=campaign_id, invite_in=invite_in)
    if not invite:
         # Může nastat, pokud kampaň mezitím zmizela (nepravděpodobné)
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return invite

@campaign_specific_invite_router.get("/", response_model=List[schemas.CampaignInvite])
async def read_campaign_invites(
    *,
    campaign_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    gm_membership: models.UserCampaign = Depends(verify_gm_permission)
):
    """
    Retrieve invites for a campaign. Requires GM role.
    """
    # Authorization checked by verify_gm_permission dependency
    invites = crud.get_invites_by_campaign(db, campaign_id=campaign_id, skip=skip, limit=limit)
    return invites

# Tento endpoint bude mít prefix /invites
@invite_router.post("/{token}/accept", response_model=schemas.CampaignInviteAcceptResponse)
def accept_invite(
    *,
    db: Session = Depends(get_db),
    token: str,
    current_user: models.User = Depends(get_current_user)
):
    """
    Accept a campaign invite using the token. Adds the current user to the campaign.
    """
    invite = crud.get_invite_by_token(db, token=token)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    success, message, campaign_id, role = crud.accept_campaign_invite(db=db, invite=invite, user_id=current_user.id)

    if not success:
        # Handle different failure reasons appropriately
        if "already a member" in message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        elif "expired" in message or "maximum number of uses" in message:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=message)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

    return schemas.CampaignInviteAcceptResponse(message=message, campaign_id=campaign_id, role=role)

# Tento endpoint bude mít také prefix /invites
@invite_router.delete("/{invite_id}", response_model=schemas.CampaignInvite)
async def delete_invite(
    *,
    db: Session = Depends(get_db),
    invite_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a campaign invite. Requires GM role for the associated campaign.
    """
    # Získáme pozvánku
    db_invite = db.query(models.CampaignInvite).filter(models.CampaignInvite.id == invite_id).first()
    if not db_invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    # Ověříme GM oprávnění pro danou kampaň manuálně
    gm_membership = crud.get_campaign_membership(db, campaign_id=db_invite.campaign_id, user_id=current_user.id)
    if not gm_membership or gm_membership.role != CampaignRoleEnum.GM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (GM required)")

    # Smažeme pozvánku
    deleted_invite = crud.delete_campaign_invite(db=db, invite_id=invite_id)
    # crud vrací None, pokud nenajde, ale už jsme ověřili
    return deleted_invite 