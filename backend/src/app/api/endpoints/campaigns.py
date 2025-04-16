from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ... import crud, models, schemas
from ...db.session import get_db
from ...auth.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Campaign)
def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Create new campaign within a world owned by the user.
    """
     # CRUD funkce create_campaign již obsahuje kontrolu vlastnictví světa
    campaign = crud.create_campaign(db=db, campaign=campaign_in, owner_id=current_user.id)
    if not campaign:
         # Pokud create_campaign vrátí None, znamená to, že svět nebyl nalezen nebo nepatří uživateli
        raise HTTPException(status_code=404, detail="World not found or access denied")
    return campaign

@router.get("/", response_model=List[schemas.Campaign])
def read_campaigns(
    db: Session = Depends(get_db),
    world_id: Optional[int] = None, # Možnost filtrovat podle světa
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve campaigns. Can be filtered by world_id.
    Only returns campaigns owned by the user or campaigns in worlds owned by the user.
    """
    if world_id:
        world = crud.get_world(db, world_id=world_id)
        if not world:
             raise HTTPException(status_code=404, detail="World not found")
        if world.owner_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not enough permissions to access this world's campaigns")
        campaigns = crud.get_campaigns_by_world(db, world_id=world_id, skip=skip, limit=limit)
    else:
         # Vrátí všechny kampaně vlastněné uživatelem napříč světy
        campaigns = crud.get_campaigns_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return campaigns


@router.get("/{campaign_id}", response_model=schemas.Campaign)
def read_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get campaign by ID.
    """
    campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
     # Ověření, zda uživatel vlastní kampaň NEBO svět, ke kterému kampaň patří
    world = crud.get_world(db, world_id=campaign.world_id)
    if campaign.owner_id != current_user.id and (not world or world.owner_id != current_user.id) :
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return campaign

@router.put("/{campaign_id}", response_model=schemas.Campaign)
def update_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: int,
    campaign_in: schemas.CampaignUpdate,
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a campaign.
    """
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Oprávnění: Uživatel musí vlastnit kampaň pro úpravu
    if db_campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

     # Zabráníme změně world_id přes tento endpoint pro jednoduchost
    if campaign_in.dict(exclude_unset=True).get("world_id") is not None:
         raise HTTPException(status_code=400, detail="Cannot change world_id via this endpoint")

    campaign = crud.update_campaign(db=db, db_campaign=db_campaign, campaign_in=campaign_in)
    return campaign

@router.delete("/{campaign_id}", response_model=schemas.Campaign)
def delete_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_id: int,
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a campaign.
    """
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Oprávnění: Uživatel musí vlastnit kampaň pro smazání
    if db_campaign.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    campaign = crud.delete_campaign(db=db, db_campaign=db_campaign)
    return campaign 