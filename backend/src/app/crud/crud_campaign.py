from sqlalchemy.orm import Session, joinedload
from ..models import World, Campaign, UserCampaign, WorldUser # Přidán WorldUser
from ..models.user_campaign import CampaignRoleEnum
from ..models.world_user import RoleEnum as WorldRoleEnum # Enum pro role ve světě
from ..schemas.campaign import CampaignCreate, CampaignUpdate

def get_campaign(db: Session, campaign_id: int):
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()

def get_campaigns_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    return db.query(Campaign).filter(Campaign.world_id == world_id).offset(skip).limit(limit).all()

def get_campaigns_by_owner(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get campaigns where the user has the GM role."""
    # Najdeme asociace, kde je uživatel GM
    gm_associations = (
        db.query(UserCampaign.campaign_id)
        .filter(UserCampaign.user_id == user_id, UserCampaign.role == CampaignRoleEnum.GM)
        .subquery()
    )
    # Vrátíme kampaně, jejichž ID jsou v seznamu GM kampaní
    return (
        db.query(Campaign)
        .filter(Campaign.id.in_(gm_associations))
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_campaign(db: Session, campaign: CampaignCreate, creator_id: int):
    """Creates a campaign, assigns creator as GM, and checks world ownership."""
    # Ověření, zda svět existuje A zda je tvůrce kampaně vlastníkem světa
    world_membership = (
        db.query(WorldUser)
        .filter(
            WorldUser.world_id == campaign.world_id,
            WorldUser.user_id == creator_id,
            WorldUser.role == WorldRoleEnum.OWNER # Ověření role OWNER ve světě
        )
        .first()
    )
    if not world_membership:
        # Svět neexistuje nebo uživatel není jeho vlastníkem
        return None # API vrstva vyhodí 403 nebo 404

    # Vytvoření kampaně bez owner_id
    db_campaign = Campaign(**campaign.dict())

    # Vytvoření GM asociace
    gm_association = UserCampaign(
        user_id=creator_id,
        campaign=db_campaign,
        role=CampaignRoleEnum.GM
    )

    db.add(db_campaign)
    db.add(gm_association)
    try:
        db.commit()
        db.refresh(db_campaign)
    except Exception as e:
        db.rollback()
        print(f"Error creating campaign or GM association: {e}")
        raise
    return db_campaign

def update_campaign(db: Session, db_campaign: Campaign, campaign_in: CampaignUpdate):
    """Updates a campaign. Assumes authorization (GM role) check happened in API layer."""
    update_data = campaign_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        # Zabráníme změně world_id přes tento endpoint
        if key == 'world_id':
            continue # Ignorujeme pokus o změnu world_id
        setattr(db_campaign, key, value)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: Campaign):
    """Deletes a campaign. Assumes authorization (GM role) check happened in API layer."""
    db.delete(db_campaign)
    db.commit()
    return db_campaign 