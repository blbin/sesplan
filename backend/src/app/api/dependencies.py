from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Use absolute imports from the 'app' package
from app import crud, models
from app.db.session import get_db
from app.auth.auth import get_current_user
from app.models.user_campaign import CampaignRoleEnum

# Helper function to check campaign membership/role (GM)
async def verify_gm_permission(campaign_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = crud.get_campaign_membership(db, campaign_id=campaign_id, user_id=current_user.id)
    if not membership or membership.role != CampaignRoleEnum.GM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions (GM required)")
    return membership # Můžeme vrátit členství pro případné další použití

# Sem můžeme v budoucnu přidat další sdílené závislosti/helpery pro API 