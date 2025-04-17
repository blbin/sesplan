from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from ..models import UserCampaign, Campaign
from ..models.user_campaign import CampaignRoleEnum
from ..schemas import UserCampaignUpdate

def get_campaign_members(db: Session, campaign_id: int, skip: int = 0, limit: int = 100):
    """Gets all members (UserCampaign associations) for a specific campaign, including user details."""
    return (
        db.query(UserCampaign)
        .options(joinedload(UserCampaign.user)) # Eager load user details
        .filter(UserCampaign.campaign_id == campaign_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_campaign_membership(db: Session, campaign_id: int, user_id: int):
    """Gets a specific UserCampaign association."""
    return (
        db.query(UserCampaign)
        .filter(UserCampaign.campaign_id == campaign_id, UserCampaign.user_id == user_id)
        .first()
    )

def update_campaign_member_role(db: Session, campaign_id: int, user_id: int, role_update: UserCampaignUpdate):
    """Updates the role of a campaign member. Returns the updated association or None."""
    db_membership = get_campaign_membership(db, campaign_id, user_id)
    if not db_membership:
        return None # Membership not found

    # Prevent changing the role of the last GM
    if db_membership.role == CampaignRoleEnum.GM:
        gm_count = (
            db.query(func.count(UserCampaign.id))
            .filter(
                UserCampaign.campaign_id == campaign_id,
                UserCampaign.role == CampaignRoleEnum.GM
            )
            .scalar()
        )
        if gm_count <= 1 and role_update.role != CampaignRoleEnum.GM:
            # Cannot change role of the last GM to something else
            return "Cannot change role of the last GM."

    db_membership.role = role_update.role
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def remove_campaign_member(db: Session, campaign_id: int, user_id_to_remove: int):
    """Removes a user from a campaign. Returns True on success, False if not found, or string message on error."""
    db_membership = get_campaign_membership(db, campaign_id, user_id_to_remove)
    if not db_membership:
        return False # Membership not found

    # Prevent removing the last GM
    if db_membership.role == CampaignRoleEnum.GM:
        gm_count = (
            db.query(func.count(UserCampaign.id))
            .filter(
                UserCampaign.campaign_id == campaign_id,
                UserCampaign.role == CampaignRoleEnum.GM
            )
            .scalar()
        )
        if gm_count <= 1:
            return "Cannot remove the last GM from the campaign."

    db.delete(db_membership)
    db.commit()
    return True 