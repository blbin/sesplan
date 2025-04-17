import secrets
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import CampaignInvite, Campaign, UserCampaign
from ..models.user_campaign import CampaignRoleEnum
from ..schemas import CampaignInviteCreate

def _generate_unique_token(db: Session):
    """Generates a unique token for campaign invites."""
    while True:
        token = secrets.token_urlsafe(16)
        existing_invite = db.query(CampaignInvite).filter(CampaignInvite.token == token).first()
        if not existing_invite:
            return token

def get_invite_by_token(db: Session, token: str):
    """Gets a campaign invite by its token."""
    return db.query(CampaignInvite).filter(CampaignInvite.token == token).first()

def get_invites_by_campaign(db: Session, campaign_id: int, skip: int = 0, limit: int = 100):
    """Gets all invites for a specific campaign."""
    # Assumes authorization (checking if user owns campaign) happens in API layer
    return db.query(CampaignInvite).filter(CampaignInvite.campaign_id == campaign_id).offset(skip).limit(limit).all()

def create_campaign_invite(db: Session, campaign_id: int, invite_in: CampaignInviteCreate):
    """Creates a new campaign invite. Returns the invite or None if campaign not found."""
    # Authorization (checking owner) should happen in API layer before calling this
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        return None # Campaign not found

    token = _generate_unique_token(db)
    db_invite = CampaignInvite(
        campaign_id=campaign_id,
        token=token,
        max_uses=invite_in.max_uses,
        expires_at=invite_in.expires_at,
        uses=0
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    return db_invite

def accept_campaign_invite(db: Session, invite: CampaignInvite, user_id: int):
    """
    Attempts to accept a campaign invite for a user.
    Returns tuple (success: bool, message: str, campaign_id: Optional[int], role: Optional[str])
    Handles checking expiry, uses, existing membership, and adding the user.
    """
    now = datetime.datetime.now(datetime.timezone.utc)

    # Check if expired
    if invite.expires_at and invite.expires_at < now:
        return False, "Invite has expired.", None, None

    # Check if max uses reached
    if invite.max_uses is not None and invite.uses >= invite.max_uses:
        return False, "Invite has reached its maximum number of uses.", None, None

    # Check if user is already in the campaign
    existing_membership = db.query(UserCampaign).filter(
        UserCampaign.user_id == user_id,
        UserCampaign.campaign_id == invite.campaign_id
    ).first()
    if existing_membership:
        return False, "User is already a member of this campaign.", invite.campaign_id, existing_membership.role.value

    # Add user to campaign with PLAYER role
    try:
        user_campaign_entry = UserCampaign(
            user_id=user_id,
            campaign_id=invite.campaign_id,
            role=CampaignRoleEnum.PLAYER
        )
        db.add(user_campaign_entry)

        # Increment invite uses
        invite.uses += 1
        db.add(invite)

        db.commit()
        # db.refresh(user_campaign_entry) # Not strictly needed here
        # db.refresh(invite) # Not strictly needed here

        return True, "Successfully joined campaign.", invite.campaign_id, CampaignRoleEnum.PLAYER.value
    except IntegrityError:
        db.rollback()
        # This might happen in a race condition if user tries to accept twice quickly
        # or if there's another DB constraint issue.
        return False, "Failed to join campaign due to a database error.", None, None
    except Exception as e:
        db.rollback()
        # Log the exception e
        return False, f"An unexpected error occurred: {e}", None, None

def delete_campaign_invite(db: Session, invite_id: int):
    """Deletes a campaign invite by its ID. Returns the deleted invite or None."""
    # Assumes authorization happens in API layer
    db_invite = db.query(CampaignInvite).filter(CampaignInvite.id == invite_id).first()
    if db_invite:
        db.delete(db_invite)
        db.commit()
        return db_invite
    return None 