from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    is_private = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    world = relationship("World", back_populates="campaigns")
    user_associations = relationship("UserCampaign", back_populates="campaign", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")
    campaign_invites = relationship("CampaignInvite", back_populates="campaign", cascade="all, delete-orphan")

    # Relationships will be added later
    # world = relationship("World", back_populates="campaigns")
    # user_associations = relationship("UserCampaign", back_populates="campaign")
    # sessions = relationship("Session", back_populates="campaign")
    # campaign_invites = relationship("CampaignInvite", back_populates="campaign") 