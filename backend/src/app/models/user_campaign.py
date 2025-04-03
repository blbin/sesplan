from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..db.session import Base
import enum

# Assuming similar roles as WorldUser, adjust if campaign roles are different
class CampaignRoleEnum(enum.Enum):
    GM = 'gm'  # Dungeon Master / Game Master
    PLAYER = 'player'
    SPECTATOR = 'spectator'

class UserCampaign(Base):
    __tablename__ = "user_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    role = Column(SQLEnum(CampaignRoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # user = relationship("User", back_populates="campaign_associations")
    # campaign = relationship("Campaign", back_populates="user_associations") 