from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class CampaignInvite(Base):
    __tablename__ = "campaign_invites"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    max_uses = Column(Integer)
    uses = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # campaign = relationship("Campaign", back_populates="campaign_invites") 