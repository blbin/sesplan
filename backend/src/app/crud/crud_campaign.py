from sqlalchemy.orm import Session
from ..models.campaign import Campaign
from ..models.world import World # Potřebujeme pro ověření vlastnictví světa
from ..schemas.campaign import CampaignCreate, CampaignUpdate

def get_campaign(db: Session, campaign_id: int):
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()

def get_campaigns_by_world(db: Session, world_id: int, skip: int = 0, limit: int = 100):
    return db.query(Campaign).filter(Campaign.world_id == world_id).offset(skip).limit(limit).all()

def get_campaigns_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
     # Získá kampaně, kde je uživatel přímým vlastníkem
    return db.query(Campaign).filter(Campaign.owner_id == owner_id).offset(skip).limit(limit).all()

# Upravená funkce pro vytvoření kampaně
def create_campaign(db: Session, campaign: CampaignCreate, owner_id: int):
     # Ověření, zda svět existuje a patří uživateli (nebo je veřejný atd. - zjednodušeno na vlastnictví)
    db_world = db.query(World).filter(World.id == campaign.world_id).first()
    if not db_world or db_world.owner_id != owner_id:
         # Můžeme zde vyhodit výjimku nebo vrátit None/False
         # Pro API je lepší vyhodit HTTP výjimku
        return None # Nebo raise HTTPException(status_code=404, detail="World not found or not owned by user")

    db_campaign = Campaign(**campaign.dict(), owner_id=owner_id)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update_campaign(db: Session, db_campaign: Campaign, campaign_in: CampaignUpdate):
    update_data = campaign_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: Campaign):
    db.delete(db_campaign)
    db.commit()
    return db_campaign 